# Embedding Preloading: Methodology and Results

## Overview

Context-Fabric (CF) uses memory-mapped CSR (Compressed Sparse Row) arrays for embedding relationships (`levUp` and `levDown`). While memory-mapping provides excellent memory efficiency, it introduces latency for embedding-heavy queries due to page faults. Preloading the CSR data into RAM trades memory for speed.

This document explains the methodology and presents benchmark results that justify making preloading the default behavior.

## Methodology

### How Embedding Queries Work

Embedding queries use the `[[` (contains) and `]]` (contained by) relations to navigate hierarchical relationships between nodes. For example:

- `clause [[ word` - Find clauses containing words
- `word ]] sentence` - Find words contained in sentences

These queries traverse the `levUp` (embedders) and `levDown` (embeddees) CSR structures.

### Memory-Mapped vs Preloaded Access

| Mode | Description | Memory | Access Pattern |
|------|-------------|--------|----------------|
| **mmap** | CSR data stays on disk, loaded on-demand | Minimal (~0 MB) | Page faults on access |
| **preload** | CSR data copied to RAM | ~100 MB for BHSA | Direct RAM access |

### Preloading Implementation

Preloading is controlled by the `CF_EMBEDDING_CACHE` environment variable:

- `CF_EMBEDDING_CACHE=on` (default): Auto-preload on corpus load
- `CF_EMBEDDING_CACHE=off`: Use mmap-only access

When enabled, `api.C.levUp.preload()` and `api.C.levDown.preload()` are called automatically during corpus loading.

## Trade-off Analysis

### Memory Cost

For the BHSA (Biblia Hebraica Stuttgartensia Amstelodamensis) corpus:

| Component | Memory |
|-----------|--------|
| `levUp` (embedders) | ~60 MB |
| `levDown` (embeddees) | ~40 MB |
| **Total** | **~100 MB** |

This is a modest cost on modern systems with 8-64 GB RAM.

### Performance Gain

**Benchmark Data:**

- Without preloading: `benchmark_results/2026-01-08_221518/latency_statistics.csv`
- With preloading: `benchmark_results/2026-01-09_010745/latency_statistics.csv`

**Key Observations:**

1. **Simple structural queries** (e.g., struct_001-019): CF is faster than TF due to the addition of vectorized lookups
2. **Embedding-heavy queries** (e.g., struct_020+): Without preloading, CF is significantly slower than TF due to mmap page faults
3. **With preloading**: CF performance is competitive with TF for embedding-heavy queries

Based on benchmark results, embedding-heavy queries show significant improvement:

**Query type:** struct_020 (structural query with embedding relations)

| Implementation | Time | vs Text-Fabric |
|----------------|------|----------------|
| Text-Fabric (TF) | 204 ms | baseline |
| CF (no preload) | 422 ms | 2.07x slower |
| CF (with preload) | 245 ms | 1.22x slower |

**Speedup from preloading:** 422 ms → 245 ms = **1.72x faster**


### Why CF is Still Slower Than TF for Some Queries

CF's search implementation differs from TF in optimization strategies. Some complex queries may still be slower due to:

- Different query execution order
- Different relation spinning algorithms
- CSR access patterns vs TF's dict-based approach

The preloading primarily eliminates the mmap page fault overhead, bringing CF closer to TF performance for embedding operations.

## Conclusion

Preloading embedding structures is now the **default behavior** in Context-Fabric because:

1. **Modest memory cost** (~100 MB for BHSA)
2. **Significant speedup** (~1.7x for embedding-heavy queries)
3. **Opt-out available** via `CF_EMBEDDING_CACHE=off`

For memory-constrained environments, disable preloading:

```bash
export CF_EMBEDDING_CACHE=off
```

For performance-critical applications, the default preloading behavior is recommended.
