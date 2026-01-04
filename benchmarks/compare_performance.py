#!/usr/bin/env python3
"""
Performance Comparison: Text-Fabric vs Context-Fabric

This benchmark compares loading performance and memory consumption between:
- Text-Fabric (TF): Original implementation using pickle/gzip caching
- Context-Fabric (CF): New implementation using memory-mapped numpy arrays

Usage:
    python benchmarks/compare_performance.py [--source PATH] [--output DIR] [--workers N]

Requirements:
    pip install text-fabric seaborn pandas matplotlib
"""

import argparse
import gc
import multiprocessing as mp
import os
import shutil
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psutil
import seaborn as sns

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'packages'))

# Default BHSA source path
DEFAULT_SOURCE = '/Users/cody/github/etcbc/bhsa/tf/2021'


@dataclass
class CorpusStats:
    """Statistics about the loaded corpus."""
    name: str = ""
    max_slot: int = 0
    max_node: int = 0
    node_types: int = 0
    node_features: int = 0
    edge_features: int = 0


@dataclass
class BenchmarkResult:
    """Store benchmark results for one implementation."""
    name: str
    compile_time: float = 0.0
    load_time: float = 0.0
    memory_before: float = 0.0
    memory_after: float = 0.0
    cache_size: float = 0.0
    corpus_stats: CorpusStats = field(default_factory=CorpusStats)

    @property
    def memory_used(self) -> float:
        return self.memory_after - self.memory_before


@dataclass
class ParallelResult:
    """Store parallel worker benchmark results."""
    name: str
    num_workers: int
    total_memory_mb: float
    per_worker_memory_mb: float
    load_time: float


def get_memory_mb() -> float:
    """Get current process memory usage in MB."""
    return psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024


def get_total_memory_mb(pids: List[int]) -> float:
    """Get total memory usage across multiple processes in MB."""
    total = 0.0
    for pid in pids:
        try:
            proc = psutil.Process(pid)
            total += proc.memory_info().rss / 1024 / 1024
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return total


def get_dir_size_mb(path: Path) -> float:
    """Get total size of directory in MB."""
    if not path.exists():
        return 0.0
    total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
    return total / 1024 / 1024


def clear_caches(source: str) -> None:
    """Remove TF and CF cache directories."""
    for cache_name in ['.tf', '.cfm']:
        cache_path = Path(source) / cache_name
        if cache_path.exists():
            shutil.rmtree(cache_path)
            print(f"  Removed: {cache_path}")


def get_corpus_name(source: str) -> str:
    """Extract corpus name from path."""
    parts = Path(source).parts
    # Look for common corpus indicators
    for i, part in enumerate(parts):
        if part in ('tf', 'text-fabric-data'):
            if i > 0:
                return parts[i-1].upper()
    return Path(source).parent.name.upper()


def benchmark_text_fabric(source: str) -> BenchmarkResult:
    """Benchmark Text-Fabric loading."""
    from tf.fabric import Fabric as TFFabric

    result = BenchmarkResult("Text-Fabric")
    tf_cache = Path(source) / '.tf'

    # Measure compile (first load)
    gc.collect()
    result.memory_before = get_memory_mb()
    print("  Compiling (first load)...")

    start = time.perf_counter()
    tf = TFFabric(locations=source, silent='deep')
    api = tf.loadAll(silent='deep')
    result.compile_time = time.perf_counter() - start

    result.memory_after = get_memory_mb()
    result.cache_size = get_dir_size_mb(tf_cache)

    # Collect corpus stats
    stats = CorpusStats(
        name=get_corpus_name(source),
        max_slot=api.F.otype.maxSlot,
        max_node=api.F.otype.maxNode,
        node_types=len(api.F.otype.all),
        node_features=len([f for f in dir(api.F) if not f.startswith('_')]),
        edge_features=len([f for f in dir(api.E) if not f.startswith('_')]),
    )
    result.corpus_stats = stats
    print(f"    Nodes: {stats.max_node:,} | Features: {stats.node_features} node, {stats.edge_features} edge")

    # Cleanup
    del tf, api
    gc.collect()

    # Measure reload (from cache)
    print("  Loading from cache...")
    start = time.perf_counter()
    tf2 = TFFabric(locations=source, silent='deep')
    api2 = tf2.loadAll(silent='deep')
    result.load_time = time.perf_counter() - start

    del tf2, api2
    gc.collect()

    return result


def benchmark_context_fabric(source: str) -> BenchmarkResult:
    """Benchmark Context-Fabric loading."""
    from cfabric.core.fabric import Fabric as CFFabric

    result = BenchmarkResult("Context-Fabric")
    cf_cache = Path(source) / '.cfm'

    # Clear CF cache for fresh compile
    if cf_cache.exists():
        shutil.rmtree(cf_cache)

    # Measure compile (first load)
    gc.collect()
    result.memory_before = get_memory_mb()
    print("  Compiling (first load)...")

    start = time.perf_counter()
    tf = CFFabric(locations=source, silent='deep')
    api = tf.load('')
    result.compile_time = time.perf_counter() - start

    result.memory_after = get_memory_mb()
    result.cache_size = get_dir_size_mb(cf_cache)

    # Collect corpus stats
    stats = CorpusStats(
        name=get_corpus_name(source),
        max_slot=api.F.otype.maxSlot,
        max_node=api.F.otype.maxNode,
        node_types=len(api.F.otype.all),
        node_features=len([f for f in dir(api.F) if not f.startswith('_')]),
        edge_features=len([f for f in dir(api.E) if not f.startswith('_')]),
    )
    result.corpus_stats = stats
    print(f"    Nodes: {stats.max_node:,} | Features: {stats.node_features} node, {stats.edge_features} edge")

    # Cleanup
    del tf, api
    gc.collect()

    # Measure reload (from cache)
    print("  Loading from cache...")
    start = time.perf_counter()
    tf2 = CFFabric(locations=source, silent='deep')
    api2 = tf2.load('')
    result.load_time = time.perf_counter() - start

    del tf2, api2
    gc.collect()

    return result


# Worker functions for parallel benchmark
def _tf_worker(source: str, ready_event, start_event, result_queue):
    """Text-Fabric worker process."""
    from tf.fabric import Fabric as TFFabric

    # Load the corpus
    tf = TFFabric(locations=source, silent='deep')
    api = tf.loadAll(silent='deep')

    # Signal ready and wait for start
    ready_event.set()
    start_event.wait()

    # Do some work to ensure data is accessed
    count = sum(1 for n in range(1, min(1000, api.F.otype.maxSlot + 1)) if api.F.otype.v(n))

    # Report memory
    mem = get_memory_mb()
    result_queue.put((os.getpid(), mem, count))

    # Wait a bit for memory measurement
    time.sleep(2)


def _cf_worker(source: str, ready_event, start_event, result_queue):
    """Context-Fabric worker process."""
    from cfabric.core.fabric import Fabric as CFFabric

    # Load the corpus
    tf = CFFabric(locations=source, silent='deep')
    api = tf.load('')

    # Signal ready and wait for start
    ready_event.set()
    start_event.wait()

    # Do some work to ensure data is accessed
    count = sum(1 for n in range(1, min(1000, api.F.otype.maxSlot + 1)) if api.F.otype.v(n))

    # Report memory
    mem = get_memory_mb()
    result_queue.put((os.getpid(), mem, count))

    # Wait a bit for memory measurement
    time.sleep(2)


def benchmark_parallel(source: str, num_workers: int = 4) -> tuple:
    """Benchmark parallel worker memory usage."""
    print(f"\n  Spawning {num_workers} workers...")

    results = {}

    for name, worker_fn in [("Text-Fabric", _tf_worker), ("Context-Fabric", _cf_worker)]:
        print(f"  [{name}] Starting {num_workers} parallel workers...")

        ctx = mp.get_context('spawn')
        ready_events = [ctx.Event() for _ in range(num_workers)]
        start_event = ctx.Event()
        result_queue = ctx.Queue()

        # Start workers
        start_time = time.perf_counter()
        processes = []
        for i in range(num_workers):
            p = ctx.Process(target=worker_fn, args=(source, ready_events[i], start_event, result_queue))
            p.start()
            processes.append(p)

        # Wait for all workers to be ready
        for evt in ready_events:
            evt.wait(timeout=120)

        load_time = time.perf_counter() - start_time

        # Signal all workers to proceed
        start_event.set()

        # Collect results
        worker_results = []
        for _ in range(num_workers):
            try:
                worker_results.append(result_queue.get(timeout=30))
            except:
                pass

        # Measure total memory across all workers
        pids = [p.pid for p in processes]
        total_mem = get_total_memory_mb(pids)

        # Wait for processes to finish
        for p in processes:
            p.join(timeout=10)
            if p.is_alive():
                p.terminate()

        per_worker = total_mem / num_workers if num_workers > 0 else 0
        print(f"    Total memory: {total_mem:.0f} MB ({per_worker:.0f} MB/worker)")

        results[name] = ParallelResult(
            name=name,
            num_workers=num_workers,
            total_memory_mb=total_mem,
            per_worker_memory_mb=per_worker,
            load_time=load_time
        )

    return results.get("Text-Fabric"), results.get("Context-Fabric")


def create_results_table(tf_result: BenchmarkResult, cf_result: BenchmarkResult) -> pd.DataFrame:
    """Create results comparison table."""
    data = {
        'Metric': [
            'Compile Time (s)',
            'Load Time (s)',
            'Memory Used (MB)',
            'Cache Size (MB)'
        ],
        'Text-Fabric': [
            tf_result.compile_time,
            tf_result.load_time,
            tf_result.memory_used,
            tf_result.cache_size
        ],
        'Context-Fabric': [
            cf_result.compile_time,
            cf_result.load_time,
            cf_result.memory_used,
            cf_result.cache_size
        ]
    }

    df = pd.DataFrame(data)

    # Calculate improvement
    improvements = []
    for i, metric in enumerate(df['Metric']):
        tf_val = df.iloc[i]['Text-Fabric']
        cf_val = df.iloc[i]['Context-Fabric']

        if 'Time' in metric:
            ratio = tf_val / cf_val if cf_val > 0 else 0
            if ratio > 1:
                improvements.append(f"{ratio:.2f}x faster")
            else:
                improvements.append(f"{1/ratio:.2f}x slower")
        elif 'Memory' in metric:
            reduction = (1 - cf_val / tf_val) * 100 if tf_val > 0 else 0
            if reduction > 0:
                improvements.append(f"{reduction:.1f}% less")
            else:
                improvements.append(f"{-reduction:.1f}% more")
        else:
            ratio = cf_val / tf_val if tf_val > 0 else 0
            if ratio > 1:
                improvements.append(f"{ratio:.1f}x larger")
            else:
                improvements.append(f"{1/ratio:.1f}x smaller")

    df['CF Improvement'] = improvements
    return df


def create_charts(tf_result: BenchmarkResult, cf_result: BenchmarkResult,
                  output_dir: Path, parallel_tf: ParallelResult = None,
                  parallel_cf: ParallelResult = None) -> None:
    """Create performance comparison charts with dark mode."""
    # Set dark mode style
    plt.style.use('dark_background')
    sns.set_theme(style="darkgrid", rc={
        "axes.facecolor": "#1a1a2e",
        "figure.facecolor": "#0f0f1a",
        "grid.color": "#2a2a4a",
        "text.color": "#e0e0e0",
        "axes.labelcolor": "#e0e0e0",
        "xtick.color": "#e0e0e0",
        "ytick.color": "#e0e0e0"
    })

    colors = ['#ff6b6b', '#4ecdc4']  # Red for TF, Teal for CF

    # Determine layout based on whether we have parallel results
    if parallel_tf and parallel_cf:
        fig, axes = plt.subplots(2, 3, figsize=(18, 11))
        axes = axes.flatten()
    else:
        fig, axes = plt.subplots(2, 2, figsize=(14, 11))
        axes = axes.flatten()

    corpus_name = tf_result.corpus_stats.name or "Corpus"
    fig.suptitle(f'Context-Fabric vs Text-Fabric Performance\n{corpus_name}: {tf_result.corpus_stats.max_node:,} nodes, {tf_result.corpus_stats.node_features} features',
                 fontsize=18, fontweight='bold', color='white', y=0.98)

    # 1. Load Time Comparison
    ax1 = axes[0]
    times = [tf_result.load_time, cf_result.load_time]
    bars1 = ax1.bar(['Text-Fabric', 'Context-Fabric'], times, color=colors, edgecolor='white', linewidth=2)
    ax1.set_ylabel('Time (seconds)', fontsize=14)
    ax1.set_title('Cache Load Time', fontsize=16, fontweight='bold', pad=15)
    ax1.tick_params(axis='both', labelsize=13)
    ax1.set_ylim(0, max(times) * 1.35)
    for bar, val in zip(bars1, times):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(times)*0.05,
                f'{val:.2f}s', ha='center', va='bottom', fontsize=15, fontweight='bold')
    speedup = tf_result.load_time / cf_result.load_time
    ax1.text(0.5, 0.92, f'{speedup:.1f}x faster', transform=ax1.transAxes,
             ha='center', va='top', fontsize=16, color='#4ecdc4', fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='#1a1a2e', edgecolor='#4ecdc4', alpha=0.8))

    # 2. Memory Usage Comparison
    ax2 = axes[1]
    memory = [tf_result.memory_used, cf_result.memory_used]
    bars2 = ax2.bar(['Text-Fabric', 'Context-Fabric'], memory, color=colors, edgecolor='white', linewidth=2)
    ax2.set_ylabel('Memory (MB)', fontsize=14)
    ax2.set_title('Memory Usage', fontsize=16, fontweight='bold', pad=15)
    ax2.tick_params(axis='both', labelsize=13)
    ax2.set_ylim(0, max(memory) * 1.35)
    for bar, val in zip(bars2, memory):
        label = f'{val:.0f} MB' if val < 1000 else f'{val/1024:.1f} GB'
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(memory)*0.05,
                label, ha='center', va='bottom', fontsize=15, fontweight='bold')
    reduction = (1 - cf_result.memory_used / tf_result.memory_used) * 100
    ax2.text(0.5, 0.92, f'{reduction:.0f}% reduction', transform=ax2.transAxes,
             ha='center', va='top', fontsize=16, color='#4ecdc4', fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='#1a1a2e', edgecolor='#4ecdc4', alpha=0.8))

    # 3. Compile Time Comparison
    ax3 = axes[2]
    compile_times = [tf_result.compile_time, cf_result.compile_time]
    bars3 = ax3.bar(['Text-Fabric', 'Context-Fabric'], compile_times, color=colors, edgecolor='white', linewidth=2)
    ax3.set_ylabel('Time (seconds)', fontsize=14)
    ax3.set_title('Initial Compile Time', fontsize=16, fontweight='bold', pad=15)
    ax3.tick_params(axis='both', labelsize=13)
    ax3.set_ylim(0, max(compile_times) * 1.35)
    for bar, val in zip(bars3, compile_times):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(compile_times)*0.05,
                f'{val:.1f}s', ha='center', va='bottom', fontsize=15, fontweight='bold')

    # 4. Cache Size Comparison
    ax4 = axes[3]
    cache_sizes = [tf_result.cache_size, cf_result.cache_size]
    bars4 = ax4.bar(['Text-Fabric', 'Context-Fabric'], cache_sizes, color=colors, edgecolor='white', linewidth=2)
    ax4.set_ylabel('Size (MB)', fontsize=14)
    ax4.set_title('Cache Size on Disk', fontsize=16, fontweight='bold', pad=15)
    ax4.tick_params(axis='both', labelsize=13)
    ax4.set_ylim(0, max(cache_sizes) * 1.35)
    for bar, val in zip(bars4, cache_sizes):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(cache_sizes)*0.05,
                f'{val:.0f} MB', ha='center', va='bottom', fontsize=15, fontweight='bold')

    # 5 & 6. Parallel worker results (if available)
    if parallel_tf and parallel_cf:
        # Parallel memory comparison
        ax5 = axes[4]
        par_mem = [parallel_tf.total_memory_mb, parallel_cf.total_memory_mb]
        bars5 = ax5.bar(['Text-Fabric', 'Context-Fabric'], par_mem, color=colors, edgecolor='white', linewidth=2)
        ax5.set_ylabel('Total Memory (MB)', fontsize=14)
        ax5.set_title(f'Parallel Memory ({parallel_tf.num_workers} Workers)', fontsize=16, fontweight='bold', pad=15)
        ax5.tick_params(axis='both', labelsize=13)
        ax5.set_ylim(0, max(par_mem) * 1.35)
        for bar, val in zip(bars5, par_mem):
            label = f'{val:.0f} MB' if val < 1000 else f'{val/1024:.1f} GB'
            ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(par_mem)*0.05,
                    label, ha='center', va='bottom', fontsize=15, fontweight='bold')
        if parallel_tf.total_memory_mb > 0:
            mem_savings = (1 - parallel_cf.total_memory_mb / parallel_tf.total_memory_mb) * 100
            ax5.text(0.5, 0.92, f'{mem_savings:.0f}% less memory', transform=ax5.transAxes,
                     ha='center', va='top', fontsize=16, color='#4ecdc4', fontweight='bold',
                     bbox=dict(boxstyle='round', facecolor='#1a1a2e', edgecolor='#4ecdc4', alpha=0.8))

        # Per-worker memory
        ax6 = axes[5]
        per_worker = [parallel_tf.per_worker_memory_mb, parallel_cf.per_worker_memory_mb]
        bars6 = ax6.bar(['Text-Fabric', 'Context-Fabric'], per_worker, color=colors, edgecolor='white', linewidth=2)
        ax6.set_ylabel('Memory per Worker (MB)', fontsize=14)
        ax6.set_title('Memory per Worker', fontsize=16, fontweight='bold', pad=15)
        ax6.tick_params(axis='both', labelsize=13)
        ax6.set_ylim(0, max(per_worker) * 1.35)
        for bar, val in zip(bars6, per_worker):
            label = f'{val:.0f} MB' if val < 1000 else f'{val/1024:.1f} GB'
            ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(per_worker)*0.05,
                    label, ha='center', va='bottom', fontsize=15, fontweight='bold')
        ax6.text(0.5, 0.92, 'mmap = shared memory', transform=ax6.transAxes,
                 ha='center', va='top', fontsize=14, color='#4ecdc4', fontweight='bold',
                 bbox=dict(boxstyle='round', facecolor='#1a1a2e', edgecolor='#4ecdc4', alpha=0.8))

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_dir / 'performance_comparison.png', dpi=150, bbox_inches='tight',
                facecolor='#0f0f1a', edgecolor='none')
    plt.close()

    # Create normalized summary chart
    fig2, ax = plt.subplots(figsize=(12, 7))
    fig2.patch.set_facecolor('#0f0f1a')

    metrics = ['Load\nTime', 'Memory\nUsage']
    if parallel_tf and parallel_cf:
        metrics.append(f'Parallel\nMemory\n({parallel_tf.num_workers}w)')

    tf_normalized = [1.0] * len(metrics)
    cf_normalized = [
        cf_result.load_time / tf_result.load_time,
        cf_result.memory_used / tf_result.memory_used,
    ]
    if parallel_tf and parallel_cf:
        cf_normalized.append(parallel_cf.total_memory_mb / parallel_tf.total_memory_mb if parallel_tf.total_memory_mb > 0 else 1.0)

    x = np.arange(len(metrics))
    width = 0.35

    bars_tf = ax.bar(x - width/2, tf_normalized, width, label='Text-Fabric', color='#ff6b6b', edgecolor='white', linewidth=2)
    bars_cf = ax.bar(x + width/2, cf_normalized, width, label='Context-Fabric', color='#4ecdc4', edgecolor='white', linewidth=2)

    ax.set_ylabel('Relative to Text-Fabric (lower is better)', fontsize=14)
    ax.set_title(f'Context-Fabric Performance (normalized)\n{corpus_name}: {tf_result.corpus_stats.max_node:,} nodes',
                 fontsize=16, fontweight='bold', color='white', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=14)
    ax.tick_params(axis='y', labelsize=13)
    ax.legend(loc='upper right', fontsize=13)
    ax.axhline(y=1.0, color='#666666', linestyle='--', alpha=0.7, linewidth=2)
    ax.set_ylim(0, 1.4)

    for bar in bars_cf:
        height = bar.get_height()
        pct = (1 - height) * 100
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.03,
               f'{pct:.0f}%\nless', ha='center', va='bottom', fontsize=13, fontweight='bold', color='#4ecdc4')

    plt.tight_layout()
    plt.savefig(output_dir / 'performance_normalized.png', dpi=150, bbox_inches='tight',
                facecolor='#0f0f1a', edgecolor='none')
    plt.close()

    print(f"\nCharts saved to {output_dir}/")


def print_results(tf_result: BenchmarkResult, cf_result: BenchmarkResult,
                  parallel_tf: ParallelResult = None, parallel_cf: ParallelResult = None) -> None:
    """Print results to console."""
    stats = tf_result.corpus_stats

    print("\n" + "=" * 70)
    print("CORPUS INFORMATION")
    print("=" * 70)
    print(f"  Name:          {stats.name}")
    print(f"  Total nodes:   {stats.max_node:,}")
    print(f"  Slot nodes:    {stats.max_slot:,}")
    print(f"  Node types:    {stats.node_types}")
    print(f"  Node features: {stats.node_features}")
    print(f"  Edge features: {stats.edge_features}")

    print("\n" + "=" * 70)
    print("SINGLE-PROCESS RESULTS")
    print("=" * 70)

    print(f"\n{tf_result.name}:")
    print(f"  Compile time: {tf_result.compile_time:.2f}s")
    print(f"  Load time:    {tf_result.load_time:.2f}s")
    print(f"  Memory used:  {tf_result.memory_used:.1f} MB ({tf_result.memory_used/1024:.2f} GB)")
    print(f"  Cache size:   {tf_result.cache_size:.1f} MB")

    print(f"\n{cf_result.name}:")
    print(f"  Compile time: {cf_result.compile_time:.2f}s")
    print(f"  Load time:    {cf_result.load_time:.2f}s")
    print(f"  Memory used:  {cf_result.memory_used:.1f} MB")
    print(f"  Cache size:   {cf_result.cache_size:.1f} MB")

    print("\n" + "-" * 70)
    load_speedup = tf_result.load_time / cf_result.load_time
    memory_reduction = (1 - cf_result.memory_used / tf_result.memory_used) * 100
    print(f"  Load speedup:      {load_speedup:.2f}x faster")
    print(f"  Memory reduction:  {memory_reduction:.1f}%")

    if parallel_tf and parallel_cf:
        print("\n" + "=" * 70)
        print(f"PARALLEL RESULTS ({parallel_tf.num_workers} WORKERS)")
        print("=" * 70)
        print(f"\n{parallel_tf.name}:")
        print(f"  Total memory:     {parallel_tf.total_memory_mb:.0f} MB ({parallel_tf.total_memory_mb/1024:.2f} GB)")
        print(f"  Per-worker:       {parallel_tf.per_worker_memory_mb:.0f} MB")

        print(f"\n{parallel_cf.name}:")
        print(f"  Total memory:     {parallel_cf.total_memory_mb:.0f} MB")
        print(f"  Per-worker:       {parallel_cf.per_worker_memory_mb:.0f} MB")

        print("\n" + "-" * 70)
        if parallel_tf.total_memory_mb > 0:
            parallel_reduction = (1 - parallel_cf.total_memory_mb / parallel_tf.total_memory_mb) * 100
            print(f"  Parallel memory savings: {parallel_reduction:.1f}%")
            print(f"  Memory per worker ratio: {parallel_tf.per_worker_memory_mb / parallel_cf.per_worker_memory_mb:.1f}x less")

    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Benchmark Text-Fabric vs Context-Fabric')
    parser.add_argument('--source', default=DEFAULT_SOURCE, help='Path to TF source files')
    parser.add_argument('--output', default='benchmarks/results', help='Output directory for charts')
    parser.add_argument('--skip-clear', action='store_true', help='Skip clearing caches before benchmark')
    parser.add_argument('--workers', type=int, default=4, help='Number of parallel workers for mmap test')
    parser.add_argument('--skip-parallel', action='store_true', help='Skip parallel worker benchmark')
    args = parser.parse_args()

    source = args.source
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("Context-Fabric Performance Benchmark")
    print("=" * 70)
    print(f"\nSource: {source}")
    print(f"Output: {output_dir}")

    # Clear caches
    if not args.skip_clear:
        print("\nClearing caches...")
        clear_caches(source)

    # Benchmark Text-Fabric
    print("\n[1/3] Benchmarking Text-Fabric...")
    tf_result = benchmark_text_fabric(source)

    # Benchmark Context-Fabric
    print("\n[2/3] Benchmarking Context-Fabric...")
    cf_result = benchmark_context_fabric(source)

    # Parallel benchmark
    parallel_tf = None
    parallel_cf = None
    if not args.skip_parallel and args.workers > 0:
        print(f"\n[3/3] Benchmarking parallel workers ({args.workers} workers)...")
        parallel_tf, parallel_cf = benchmark_parallel(source, args.workers)

    # Print results
    print_results(tf_result, cf_result, parallel_tf, parallel_cf)

    # Create results table
    df = create_results_table(tf_result, cf_result)
    print("\nResults Table:")
    print(df.to_string(index=False))

    # Save CSV
    csv_path = output_dir / 'results.csv'
    df.to_csv(csv_path, index=False)
    print(f"\nResults saved to {csv_path}")

    # Create charts
    print("\nGenerating charts...")
    create_charts(tf_result, cf_result, output_dir, parallel_tf, parallel_cf)

    print("\nBenchmark complete!")


if __name__ == '__main__':
    main()
