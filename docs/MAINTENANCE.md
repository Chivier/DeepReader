# DeepReader maintenance

## Install and launch

Use Python 3.12 or 3.13 and an isolated virtual environment. Install `requirements.txt`, copy `.env.example` to `.env`, and set `OPENAI_API_KEY`. Environment variables override `.env`. Start the multipage app with `python -m streamlit run website/Home.py` from the repository root, or run `website/run_app.sh` from any directory after activating the environment.

Cairo is required for bookmark exports (`brew install cairo` on macOS; `apt-get install libcairo2` on Debian/Ubuntu). Optional local audio transcription additionally requires ffmpeg and `pip install -r requirements_video.txt`. The correct package is **openai-whisper**, which provides `whisper.load_model`; the unrelated `whisper` package is not supported. `WHISPER_MODEL` defaults to `base`; device selection uses CUDA when available, otherwise CPU. Bilibili downloads may use the external `lux` command; yt-dlp provides a fallback in the add-book page.

The review pipeline uses the same OpenAI-compatible endpoint and model as chat. Optional `DEEPREADER_REVIEW_MODEL` and `DEEPREADER_REPORT_MODEL` override the pipeline model. Former hardcoded Ollama/OpenRouter/Gemini settings have been removed; configure an endpoint that supports the selected model.

## Storage

- Book processing writes to `<repository>/data/books/<title>/`; override the root with `DEEPREADER_DATA_DIR`.
- Generated discussion guides stay in `website/book_prompt/`.
- Chat history and exported bookmarks stay in `website/chat_history/` and `website/bookmarks/`.
- Existing files in historical book directories are preserved. There is no automatic data migration or deletion.
- Failed processing retains collected source data and reports an error. It does not publish a placeholder as a successful guide.
- Book names are validated before filesystem operations. Model-generated SVG rejects active content, external resources, excessive elements and oversized canvases.

The app has no user authentication or tenant isolation. For personal use, bind to localhost or place it behind authenticated access. Chat files are plaintext on disk. An internet-facing multi-user service needs authentication, per-user storage, rate limits and a job queue before deployment.

## Update dependencies

`requirements.in` defines direct runtime dependencies; `requirements.txt` locks direct and transitive dependencies across platforms. The optional transcription lock shares the runtime constraints.

```bash
uv pip compile requirements.in --upgrade --python-version 3.12 --universal --output-file requirements.txt
uv pip compile requirements_video.in --upgrade --python-version 3.12 --universal --output-file requirements_video.txt
pip install -r requirements_dev.txt
pip check
python -m pytest -q
python -m compileall -q reader website
python -m reader.main --help
pip-audit -r requirements.txt --no-deps --disable-pip
pip-audit -r requirements_video.txt --no-deps --disable-pip
```

The audit checks every explicitly pinned package in each lock without downloading optional Torch/CUDA distributions. It evaluates markers for the auditing platform; the Ubuntu CI adds Linux coverage. `requirements_dev.txt` resolves testing tools separately; the application locks remain pinned. Dependabot checks pip and GitHub Actions weekly. CI runs on pushes, pull requests and weekly schedules with Python 3.12/3.13; it checks install compatibility, compilation, tests and both dependency locks.

## Verification boundaries

Offline tests exercise search parsing, network timeouts, title/path validation, worker exceptions, report location, mocked OpenAI chat, chat persistence, add-book failures, and real SVG-to-PNG/PDF conversion. They do not establish live Douban/Bilibili availability, API model quality, or local Whisper accuracy. Streamlit's UI tests use mocked API responses and never require credentials or spend API credits.

Security alerts on GitHub remain dependent on the default branch and GitHub's rescanning. A clean local audit or an unmerged maintenance branch does not prove those alerts are closed.
