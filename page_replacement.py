"""
Lab Assignment-3: Comprehensive Implementation of Page Replacement Algorithms
Course: Fundamentals of Operating System Lab (ENCA252)
Program: BCA (AI & DS) (Research)

Algorithms implemented:
  1. FIFO  - First In First Out
  2. LRU   - Least Recently Used
  3. Optimal Page Replacement
  4. MRU   - Most Recently Used
  5. Second Chance (Clock Algorithm)
"""

from collections import deque


# ─────────────────────────────────────────────────────────────
# Task 1: Input and Page Reference String
# ─────────────────────────────────────────────────────────────
def get_input():
    """Get number of frames and page reference string from the user."""
    print("=" * 55)
    print("   PAGE REPLACEMENT ALGORITHM SIMULATOR")
    print("=" * 55)

    while True:
        try:
            frames = int(input("\nEnter number of frames: "))
            if frames <= 0:
                print("  Frames must be a positive integer.")
                continue
            break
        except ValueError:
            print("  Invalid input. Please enter an integer.")

    while True:
        try:
            raw = input("Enter page reference string (space-separated): ")
            pages = list(map(int, raw.split()))
            if not pages:
                print("  Page string cannot be empty.")
                continue
            break
        except ValueError:
            print("  Invalid input. Enter integers separated by spaces.")

    print(f"\nReference String : {pages}")
    print(f"Number of Frames : {frames}")
    print("-" * 55)
    return frames, pages


# ─────────────────────────────────────────────────────────────
# Helper: pretty-print frame state after each page reference
# ─────────────────────────────────────────────────────────────
def print_table(algo_name, pages, frame_states, faults):
    print(f"\n{'─'*55}")
    print(f"  {algo_name}")
    print(f"{'─'*55}")

    # Header row
    header = "Page | " + " | ".join(f"{p:^4}" for p in pages)
    print(header)
    print("─" * len(header))

    # Determine max frames needed for display
    max_f = max(len(s) for s in frame_states) if frame_states else 0

    for row in range(max_f):
        line = "     | "
        for state in frame_states:
            if row < len(state):
                line += f"{state[row]:^4} | "
            else:
                line += "     | "
        print(line)

    print(f"\n  Total Page Faults : {faults}")


# ─────────────────────────────────────────────────────────────
# Task 2: FIFO – First In First Out
# ─────────────────────────────────────────────────────────────
def fifo(frames, pages):
    """
    Replace the page that entered memory first (oldest page).
    Uses a queue to track insertion order.
    """
    memory = []          # current pages in frames
    queue  = deque()     # tracks insertion order
    faults = 0
    frame_states = []

    for page in pages:
        if page not in memory:
            faults += 1
            if len(memory) < frames:
                memory.append(page)
                queue.append(page)
            else:
                # Remove the oldest (front of queue)
                oldest = queue.popleft()
                memory[memory.index(oldest)] = page
                queue.append(page)

        frame_states.append(list(memory))

    print_table("FIFO (First In First Out)", pages, frame_states, faults)
    return faults


# ─────────────────────────────────────────────────────────────
# Task 3: LRU – Least Recently Used
# ─────────────────────────────────────────────────────────────
def lru(frames, pages):
    """
    Replace the page that has not been used for the longest time.
    Tracks recency via a usage list.
    """
    memory = []
    faults = 0
    frame_states = []

    for i, page in enumerate(pages):
        if page not in memory:
            faults += 1
            if len(memory) < frames:
                memory.append(page)
            else:
                # Find the page used least recently
                lru_page = None
                lru_time = float('inf')
                for p in memory:
                    # Search backwards for last use
                    for j in range(i - 1, -1, -1):
                        if pages[j] == p:
                            if j < lru_time:
                                lru_time = j
                                lru_page = p
                            break
                    else:
                        # Page not used before current index
                        lru_page = p
                        break
                memory[memory.index(lru_page)] = page

        frame_states.append(list(memory))

    print_table("LRU (Least Recently Used)", pages, frame_states, faults)
    return faults


# ─────────────────────────────────────────────────────────────
# Task 4: Optimal Page Replacement
# ─────────────────────────────────────────────────────────────
def optimal(frames, pages):
    """
    Replace the page that will not be used for the longest time in the future.
    This gives the minimum possible page faults (theoretical benchmark).
    """
    memory = []
    faults = 0
    frame_states = []

    for i, page in enumerate(pages):
        if page not in memory:
            faults += 1
            if len(memory) < frames:
                memory.append(page)
            else:
                # Look ahead: find each page's next use
                farthest_page = None
                farthest_dist = -1

                for p in memory:
                    # Find next occurrence of p after position i
                    try:
                        dist = pages.index(p, i + 1)
                    except ValueError:
                        # Page never used again → replace it immediately
                        farthest_page = p
                        break
                    if dist > farthest_dist:
                        farthest_dist = dist
                        farthest_page = p

                memory[memory.index(farthest_page)] = page

        frame_states.append(list(memory))

    print_table("Optimal Page Replacement", pages, frame_states, faults)
    return faults


# ─────────────────────────────────────────────────────────────
# Task 5: MRU – Most Recently Used
# ─────────────────────────────────────────────────────────────
def mru(frames, pages):
    """
    Replace the most recently used page.
    Useful when recently used pages are unlikely to be needed again soon.
    """
    memory = []
    recent = []   # tracks usage order (last element = most recent)
    faults = 0
    frame_states = []

    for page in pages:
        if page not in memory:
            faults += 1
            if len(memory) < frames:
                memory.append(page)
            else:
                # Find the most recently used page in memory
                for p in reversed(recent):
                    if p in memory:
                        mru_page = p
                        break
                memory[memory.index(mru_page)] = page

            if page in recent:
                recent.remove(page)
            recent.append(page)
        else:
            # Update recency even on a hit
            if page in recent:
                recent.remove(page)
            recent.append(page)

        frame_states.append(list(memory))

    print_table("MRU (Most Recently Used)", pages, frame_states, faults)
    return faults


# ─────────────────────────────────────────────────────────────
# Second Chance (Clock) Algorithm
# ─────────────────────────────────────────────────────────────
def second_chance(frames, pages):
    """
    FIFO with a second-chance reference bit.
    Pages with bit=1 get one more chance before eviction.
    Simulates a hardware clock hand sweeping through frames.
    """
    memory   = []          # pages currently in frames
    ref_bits = []          # reference bit for each frame slot
    clock    = 0           # clock hand pointer
    faults   = 0
    frame_states = []

    for page in pages:
        if page in memory:
            # Hit: set reference bit
            ref_bits[memory.index(page)] = 1
        else:
            faults += 1
            if len(memory) < frames:
                memory.append(page)
                ref_bits.append(1)
            else:
                # Advance clock hand until we find a page with ref_bit = 0
                while ref_bits[clock] == 1:
                    ref_bits[clock] = 0      # give second chance
                    clock = (clock + 1) % frames

                # Replace the page at clock position
                memory[clock]   = page
                ref_bits[clock] = 1
                clock = (clock + 1) % frames

        frame_states.append(list(memory))

    print_table("Second Chance (Clock Algorithm)", pages, frame_states, faults)
    return faults


# ─────────────────────────────────────────────────────────────
# Task 6 & 7: Performance Comparison and Result Analysis
# ─────────────────────────────────────────────────────────────
def compare_algorithms(frames, pages):
    """Run all algorithms and display a comparison summary."""
    print("\n" + "=" * 55)
    print("   RUNNING ALL ALGORITHMS")
    print("=" * 55)

    results = {
        "FIFO"          : fifo(frames, pages),
        "LRU"           : lru(frames, pages),
        "Optimal"       : optimal(frames, pages),
        "MRU"           : mru(frames, pages),
        "Second Chance" : second_chance(frames, pages),
    }

    # ── Comparison Table ──────────────────────────────────────
    print("\n" + "=" * 55)
    print("   PERFORMANCE COMPARISON SUMMARY")
    print("=" * 55)
    print(f"{'Algorithm':<20} {'Page Faults':>12} {'Efficiency':>12}")
    print("-" * 46)

    total_refs = len(pages)
    for algo, faults in results.items():
        hit_rate = ((total_refs - faults) / total_refs) * 100
        print(f"{algo:<20} {faults:>12} {hit_rate:>11.1f}%")

    # ── Result Analysis ───────────────────────────────────────
    best_algo  = min(results, key=results.get)
    worst_algo = max(results, key=results.get)

    print("\n" + "=" * 55)
    print("   RESULT ANALYSIS")
    print("=" * 55)
    print(f"  Best  Algorithm : {best_algo}  ({results[best_algo]} faults)")
    print(f"  Worst Algorithm : {worst_algo} ({results[worst_algo]} faults)")

    print("""
  Conclusions
  ───────────
  • Optimal   → Theoretical minimum faults (not implementable in
                real OSes since future accesses are unknown).
                Used as a benchmark for other algorithms.

  • LRU       → Best practical algorithm; exploits temporal
                locality well. Higher overhead due to recency
                tracking.

  • FIFO      → Simplest to implement. Can suffer from Belady's
                anomaly (more frames → more faults in rare cases).

  • Second    → Approximates LRU with lower overhead by using a
    Chance      single reference bit per frame (used in Linux).

  • MRU       → Useful for sequential scans where recently used
                pages won't be needed again soon (e.g. DB scans).
    """)


# ─────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    frames, pages = get_input()
    compare_algorithms(frames, pages)
