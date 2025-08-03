#!/usr/bin/env python3
"""Performance profiling script for LiteLLM."""
import cProfile
import pstats
from pathlib import Path
from memory_profiler import profile as memory_profile
from line_profiler import LineProfiler

def profile_cpu(func):
    """Profile CPU usage of a function."""
    profiler = cProfile.Profile()
    profiler.enable()
    result = func()
    profiler.disable()
    
    # Save stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    
    output_dir = Path("profiling_results")
    output_dir.mkdir(exist_ok=True)
    stats.dump_stats(output_dir / f"{func.__name__}_cpu.prof")
    return result

def profile_memory(func):
    """Profile memory usage of a function."""
    return memory_profile(func)()

def profile_lines(func):
    """Profile line-by-line execution time."""
    profiler = LineProfiler()
    profiled_func = profiler(func)
    profiled_func()
    
    output_dir = Path("profiling_results")
    output_dir.mkdir(exist_ok=True)
    profiler.dump_stats(output_dir / f"{func.__name__}_lines.prof")

def run_profiling():
    """Run profiling on desired functions."""
    from litellm.llms.base import BaseLLM
    from litellm.main import completion
    
    # Example profiling - customize based on needs
    @profile_cpu
    def test_completion():
        completion(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello!"}])
    
    print("CPU profiling complete. Results saved in profiling_results/")

if __name__ == "__main__":
    run_profiling()