# rag-lab

Which RAG architecture gives the best answers for the cost? This study builds eight
retrieval-augmented generation architectures and measures them the same way: one corpus, one
frozen eval set, one model and one set of shared constants, so the architecture is the only thing
that differs.

This repo is the map of the study. It holds no pipeline code. It links each architecture's repo,
the shared base they build on and the benchmark that checks and judges their runs, and pins each
of them as a git submodule, so one clone fetches the whole study at a known commit of every repo.

**Try it:** a demo page on the [portfolio](https://amritesh.net), coming soon.

## The eight architectures

`simple` is the baseline, and each other architecture adds one mechanism to it. Architecture repos
depend on rag-core and override the retrieval or orchestration layer while reusing everything
else. The call column is the most model calls the pipeline can make for one question; the judge
calls an evaluation adds are counted apart.

| Architecture | What it adds to simple | Model calls per question, at most | Repo |
| ------------ | ---------------------- | --------------------------------- | ---- |
| simple | Nothing: it retrieves the top `k` chunks for the question and generates one answer from them. It is the base's own pipeline. | 1 | [rag-core](https://github.com/Amritesh-878/rag-core) |
| memory | Condenses the prior turns and the question into one standalone query before retrieval. Generation still answers the original question with the full history. | 2, and 1 when there is no history | [rag-memory](https://github.com/Amritesh-878/rag-memory) |
| hyde | Asks the model to draft the passage it expects to find and embeds that draft for retrieval instead of the question. Generation never sees the draft. | 2 | [rag-hyde](https://github.com/Amritesh-878/rag-hyde) |
| branched | Asks the model which of the corpus's three domains could answer the question, then searches only those domains' collections. | 2 | [rag-branched](https://github.com/Amritesh-878/rag-branched) |
| adaptive | Asks the model whether the question is simple or complex. A simple one is searched once; a complex one is split into two to four sub queries, each is searched, and `k` chunks are chosen across them. | 4, a ceiling checked before every call; the paths cost 2 or 3 | [rag-adaptive](https://github.com/Amritesh-878/rag-adaptive) |
| crag | Grades every retrieved chunk for relevance in one call. When fewer than three in four pass, it rewrites the question and replaces the failing chunks with fresh ones from the corpus. | 3 | [rag-crag](https://github.com/Amritesh-878/rag-crag) |
| self | Answers first, then asks in one call whether the answer is grounded in its chunks and whether they were enough. When either is no, it retrieves again with a changed query and answers once more. | 3 | [rag-self](https://github.com/Amritesh-878/rag-self) |
| agentic | Lets the model choose, turn by turn, among vector search, keyword search and document lookup over the corpus, then answers from four of the chunks it gathered. In progress: the repo answers through the base pipeline today, and the controller and its tools come next. | 8, across at most 6 turns | [rag-agentic](https://github.com/Amritesh-878/rag-agentic) |

Each repo's README explains its mechanism in depth, with worked examples and the cases where the
mechanism works against the question.

## The shared base and the benchmark

| Repo | Role |
| ---- | ---- |
| [rag-core](https://github.com/Amritesh-878/rag-core) | The shared base. It holds the constants that must stay identical across repos (chunking, embeddings, the vector store, the model, retrieval defaults and the generation system prompt), the `simple` pipeline, the corpus manifest and fetcher, and the eval harness. Every other repo installs it from a tag. |
| [rag-bench](https://github.com/Amritesh-878/rag-bench) | The benchmark. It archives results files under the digest of their bytes and refuses runs whose provenance or record shape makes them incomparable. A pooled judging pass then scores every accepted record again, with the record's architecture and its implementer kept out of what the judge sees. |

Everything that could confound a comparison comes from rag-core, so two architecture repos cannot
drift apart without it showing. A second implementer is building the same specification
independently.

## Results

The counted comparison has not run, so this page reports no scores. Each architecture repo
reports its own runs under its Measured results heading:
[memory](https://github.com/Amritesh-878/rag-memory#measured-results),
[hyde](https://github.com/Amritesh-878/rag-hyde#measured-results),
[branched](https://github.com/Amritesh-878/rag-branched#measured-results),
[adaptive](https://github.com/Amritesh-878/rag-adaptive#measured-results),
[crag](https://github.com/Amritesh-878/rag-crag#measured-results) and
[self](https://github.com/Amritesh-878/rag-self#measured-results).

Each of those sections states the conditions of its own run, such as the base version, the inputs
and the item count. A figure there describes that run alone and is not read against another
architecture's figure. `simple` has no such section, because rag-core holds the code and the
frozen inputs, not results.

## Get the whole study

```bash
git clone --recursive https://github.com/Amritesh-878/rag-lab.git
```

In a clone made without `--recursive`, `git submodule update --init` fetches the same commits.
Each `rag-*` folder at the top of this repo is a submodule pinned to one commit of its repo, and
the last commit on each folder says in one line what that repo does. `repos.toml` is the same map
in machine-readable form: each repo's name, role, URL and the rag-core tag it installs.

Install and run instructions live in each repo's own README. Nothing here needs installing to use
the study.

## Checking the map

`tests/test_links.py` fails when the README tables, `repos.toml` and `.gitmodules` stop naming the
same repos. It reads the three files and makes no network call.

```bash
uv venv -p 3.14.7 .venv
uv pip install --python .venv/Scripts/python.exe -e ".[dev]"
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m ruff format --check .
.venv/Scripts/python.exe -m mypy tests
.venv/Scripts/python.exe -m pytest -q
```
