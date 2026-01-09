# Vectorized Node Feature Lookup: Performance Analysis

## Overview

Context-Fabric (CF) stores corpus data in memory-mapped numpy arrays, achieving 90% memory reduction compared to Text-Fabric (TF). However, memory-mapping introduces latency from page faults. This document analyzes how vectorized feature lookups overcome that overhead, enabling CF to outperform TF for feature-based queries.

**Key Finding:** Vectorized lookup provides an **8.2x algorithmic speedup**, which translates to **~1.3x real-world speedup** over TF after accounting for mmap overhead.

## Background: Page Faults and Memory-Mapped Files

When an application uses memory-mapped files (mmap), the operating system creates a mapping between virtual memory addresses and the file on disk. Data is loaded on-demand when the application first accesses each memory region.

A **page fault** is an exception raised by the CPU's memory management unit (MMU) when a program accesses a virtual memory address that isn't currently mapped to physical RAM. The kernel handles this by pausing the program, loading data from disk, updating page tables, and resuming execution.

| Access Type | Latency | Relative Cost |
|-------------|---------|---------------|
| RAM access | ~70 ns | 1x |
| Minor page fault | ~1-3 μs | ~15-40x |
| Major page fault (SSD) | ~30 μs | ~400x |
| Major page fault (HDD) | ~8 ms | ~100,000x |

Per-element access patterns (like looping through nodes) can trigger thousands of page faults. Vectorized access patterns are more cache-friendly and amortize page fault costs across bulk operations.

**Sources:** [Page fault - Wikipedia](https://en.wikipedia.org/wiki/Page_fault) | [Erik Rigtorp](https://rigtorp.se/virtual-memory/) | [USENIX](https://www.usenix.org/system/files/conference/hotstorage17/hotstorage17-paper-choi.pdf) | [ACM](https://dl.acm.org/doi/full/10.1145/3547142)

## CF vs TF: Architectural Trade-offs

| | Context-Fabric | Text-Fabric |
|--|----------------|-------------|
| **Storage** | Memory-mapped numpy arrays | In-memory Python dicts |
| **Memory usage** | ~500 MB for BHSA | ~6 GB for BHSA |
| **Access pattern** | Page faults on first access | Direct RAM access |
| **Paging issues** | Yes (OS may page out data) | No (always in RAM) |

TF loads everything into RAM upfront and never suffers from paging issues. CF's memory-mapping provides 90% memory reduction but introduces latency. Vectorization is essential for CF to overcome this overhead.

## The Problem: Per-Node Looping

The original implementation (inherited from Text-Fabric) checked each node individually:

```python
# OLD approach: Per-node looping (inherited from Text-Fabric)
for n in nodeSet:
    good = True
    for ft, val in featureList:
        fval = Fs(ft).v(n)  # Per-node lookup
        if val is None:
            if fval is not None:
                good = False
                break
        elif ident:
            if fval not in val:
                good = False
                break
    if good:
        yarn.add(n)
```

This approach incurs O(n) Python function calls, each involving bounds checking, index lookup, and sentinel comparison—plus potential page faults on every access.

## The Solution: Vectorized Filtering

The new implementation processes all nodes at once using numpy:

```python
# NEW approach: Vectorized numpy operations
yarn = set(nodeSet)

for ft, val in featureList:
    feature_data = feature._data
    if is_mmap and _can_vectorize_constraint(val):
        yarn = _vectorized_filter(yarn, feature_data, val)
    else:
        yarn = _scalar_filter(yarn, feature, val)
```

The filter operates on arrays directly:

```python
def filter_by_value(self, nodes: list[int], value: str) -> NDArray[np.int64]:
    node_arr = np.asarray(nodes, dtype=np.int64)
    arr_indices = node_arr - 1

    values_at_nodes = self.indices[arr_indices]
    match_mask = values_at_nodes == value_idx

    return node_arr[match_mask]
```

Vectorization is only possible because CF stores data in numpy arrays. The same data model that enables memory-mapping also enables vectorized filtering—this is taking full advantage of CF's architecture, not just compensating for its limitations.

### Why Vectorization is Faster

1. **Reduced Python overhead**: ~3 numpy operations vs 426,590 function calls
2. **CPU cache efficiency**: Contiguous memory access benefits from prefetching
3. **SIMD operations**: Numpy leverages CPU vector instructions (SSE, AVX)
4. **Reduced branching**: Single conditional per feature vs per-node conditionals

### Constraints Supported

| Constraint Type | Example | Vectorizable |
|-----------------|---------|--------------|
| Value equals | `sp=verb` | Yes |
| Value in set | `sp=verb\|noun` | Yes |
| Value not in set | `sp!=verb` | Yes |
| Has any value | feature exists | Yes |
| Missing value | feature is None | Yes |
| Regex pattern | `lex~>^ab` | No (falls back to looping) |
| Custom function | `lambda x: x > 5` | No (falls back to looping) |

## Simulation Results

The following results come from `simulation_looping_vs_vectorized.py`, which isolates the filtering operation to measure algorithmic speedup. These are **not** from the full benchmarking suite—see `benchmark_results/` for comprehensive TF vs CF comparisons.

**Corpus:** BHSA | **Words:** 426,590 | **Iterations:** 10

| Feature | Value | Matches | Looping (ms) | Vectorized (ms) | Speedup |
|---------|-------|---------|--------------|-----------------|---------|
| sp (part of speech) | verb | 73,710 | 147.62 | 17.64 | **8.37x** |
| sp | subs (noun) | 121,509 | 148.30 | 21.97 | **6.75x** |
| sp | art (article) | 30,386 | 141.89 | 15.09 | **9.40x** |
| sp | prep | 73,273 | 143.65 | 17.54 | **8.19x** |
| sp | conj | 62,722 | 144.76 | 17.51 | **8.27x** |
| vt (verb tense) | perf | 21,129 | 152.83 | 15.15 | **10.09x** |
| vt | impf | 16,099 | 141.25 | 13.75 | **10.27x** |
| gn (gender) | m | 164,176 | 147.28 | 24.93 | **5.91x** |
| gn | f | 36,721 | 142.41 | 15.63 | **9.11x** |
| nu (number) | sg | 180,110 | 153.10 | 28.28 | **5.41x** |
| nu | pl | 54,941 | 143.62 | 17.06 | **8.42x** |

| Metric | Value |
|--------|-------|
| **Average Speedup** | 8.20x |
| **Minimum Speedup** | 5.41x |
| **Maximum Speedup** | 10.27x |

## Real-World Performance: CF vs TF

The 8.2x algorithmic speedup translates to ~1.3x real-world improvement because much of that gain is "spent" overcoming mmap overhead:

| Query | TF (dict-based) | CF (mmap + vectorized) | CF Speedup |
|-------|-----------------|------------------------|------------|
| lex_001 | 211 ms | 156 ms | **1.35x** |
| lex_011 | 246 ms | 140 ms | **1.76x** |
| struct_001 | 127 ms | 97 ms | **1.31x** |
| struct_004 | 174 ms | 91 ms | **1.91x** |

Without vectorization, CF would be slower than TF due to mmap overhead. With vectorization, CF achieves both 90% memory reduction and ~1.3x faster query performance.

## Limitation: Embedding Relations

Vectorization only optimizes **node feature filtering**. It does not help with **embedding relations** (`[[` contains, `]]` contained by) where the bottleneck is mmap page faults when traversing CSR structures.

| Query Type | CF vs TF |
|------------|----------|
| Feature lookup (vectorized) | CF **1.3x faster** |
| Embedding relations (mmap) | CF **2.07x slower** |
| Embedding relations (preloaded, +100 MB RAM) | CF **1.22x slower** |

For embedding relations, the only solution is to accept ~100 MB RAM for preloading. See [embedding_preloading.md](../embedding_preloading.md).

## Summary

| Operation | CF Challenge | Solution | RAM Cost | Algorithmic Gain | Net vs TF |
|-----------|--------------|----------|----------|------------------|-----------|
| Feature filtering | mmap overhead | Vectorization | 0 | 8.2x | **1.3x faster** |
| Embedding relations | mmap page faults | Preloading | ~100 MB | 1.7x | 1.2x slower |

## Code Changes

**`libs/core/cfabric/storage/string_pool.py`**
- Added `filter_by_value()`, `filter_by_values()`, `filter_has_value()`, `filter_missing_value()`
- Same methods added to `IntFeatureArray` class

**`libs/core/cfabric/search/spin.py`**
- Modified `_spinAtom()` to detect mmap backends and route to vectorized path
- Added `_can_vectorize_constraint()`, `_vectorized_filter()`, `_scalar_filter()`

## Reproducing the Simulation

```bash
cd /path/to/context-fabric
source .venv/bin/activate
PYTHONPATH=libs/core:libs/benchmarks python \
  libs/benchmarks/findings/vectorized-feature-lookup/simulation_looping_vs_vectorized.py
```

Results are saved to `simulation_results.json`. For full TF vs CF benchmarks, see the `cfabric_benchmarks` package.
