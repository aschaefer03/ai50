import os
import random
import re
import sys
from copy import deepcopy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    prob_dist = {}
    for site in corpus.keys():
        prob_dist[site] = 0
    if corpus.get(page) and len(corpus.get(page)) > 0:
        links = corpus.get(page)
        for link in links:
            prob_dist[link] = damping_factor * (1 / len(links))
    else:
        for site in corpus.keys():
            prob_dist[site] = 1 / len(corpus)
        return prob_dist
    for site in prob_dist.keys():
        prob_dist[site] = prob_dist.get(site) + ((1 - damping_factor) * (1 / len(prob_dist)))
    total_prob = 0
    for prob in prob_dist.values():
        total_prob += prob
    if not 1 - 1e-4 < total_prob < 1 + 1e-4:
        print(total_prob)
        raise ArithmeticError("Calculated probability not equal to 1")
    return prob_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_ranks = {}
    for site in corpus.keys():
        page_ranks[site] = 0
    site1 = random.choices(list(page_ranks.keys()))[0]
    page_ranks[site1] = 1
    site = site1
    counter = 1
    while counter < n:
        prob_dist = transition_model(corpus, site, damping_factor)
        sites = []
        weights = []
        for key, value in prob_dist.items():
            sites.append(key)
            weights.append(value)
        site = random.choices(sites, weights)[0]
        page_ranks[site] = page_ranks.get(site) + 1
        counter += 1
    ranks = 0
    for key in page_ranks.keys():
        page_ranks[key] = page_ranks.get(key) / n
        ranks += page_ranks.get(key)
    if not 1 - 1e-4 < ranks < 1 + 1e-4:
        print(ranks)
        raise ArithmeticError("Sampling page ranks did not add to 1")
    return page_ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_ranks = {}
    d = damping_factor
    n = len(corpus)
    for site in corpus.keys():
        page_ranks[site] = 1 / n
    loops = 0
    while True:
        old_ranks = deepcopy(page_ranks)
        for site in page_ranks.keys():
            sum_links = 0
            for site2 in corpus.keys():
                if site in corpus.get(site2):
                    sum_links += page_ranks.get(site2) / len(corpus.get(site2))
                elif len(corpus.get(site2)) == 0:
                    sum_links += page_ranks.get(site2) / len(corpus)
            page_ranks[site] = ((1 - d) / n) + d * sum_links
        for site in page_ranks.keys():
            if loops > 1e5:
                raise ArithmeticError
            if abs(page_ranks.get(site) - old_ranks.get(site)) > 0.001:
                loops += 1
                continue
        ranks = 0
        for key in page_ranks.keys():
            ranks += page_ranks.get(key)
        if not 1 - 1e-3 < ranks < 1 + 1e-3:
            continue
        break
    return page_ranks


if __name__ == "__main__":
    main()
