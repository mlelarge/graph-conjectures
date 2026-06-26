"""Entropy and branching diagnostics for canonical rank fibres of B_k."""

from __future__ import annotations

import math
from collections import Counter, defaultdict

from stilde_pod_profiles import layer_ranks, word


def rank_fibres(order, depth):
    ranks = [layer_ranks(order, depth, colour) for colour in range(3)]
    fibres = defaultdict(list)
    for vertex in order:
        fibres[tuple(rank[vertex] for rank in ranks)].append(word(vertex, depth))
    return fibres


def entropy_profile(order, depth):
    fibres = rank_fibres(order, depth)
    total = 3**depth
    rank_entropy = 0.0
    conditional_entropy = 0.0
    for words in fibres.values():
        probability = len(words) / total
        rank_entropy -= probability * math.log2(probability)
        conditional_entropy += probability * math.log2(len(words))

    singleton_mass_by_level = []
    conditional_bits_by_level = []
    for level in range(depth):
        singleton_mass = 0
        conditional_bits = 0.0
        for words in fibres.values():
            by_prefix = defaultdict(Counter)
            for value in words:
                by_prefix[value[:level]][value[level]] += 1
            for counts in by_prefix.values():
                mass = sum(counts.values()) / total
                if len(counts) == 1:
                    singleton_mass += mass
                entropy = 0.0
                subtotal = sum(counts.values())
                for count in counts.values():
                    probability = count / subtotal
                    entropy -= probability * math.log2(probability)
                conditional_bits += mass * entropy
        singleton_mass_by_level.append(singleton_mass)
        conditional_bits_by_level.append(conditional_bits)

    heights = [
        max(rank.values())
        for rank in [layer_ranks(order, depth, colour) for colour in range(3)]
    ]
    return {
        "depth": depth,
        "rank_entropy_bits": rank_entropy,
        "rank_entropy_per_level": rank_entropy / depth,
        "conditional_entropy_bits": conditional_entropy,
        "conditional_entropy_per_level": conditional_entropy / depth,
        "layer_heights": heights,
        "log2_height_product": sum(math.log2(height) for height in heights),
        "singleton_mass_by_level": singleton_mass_by_level,
        "conditional_bits_by_level": conditional_bits_by_level,
        "average_singleton_mass": sum(singleton_mass_by_level) / depth,
    }
