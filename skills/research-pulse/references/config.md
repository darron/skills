# Config

The CLI resolves config in this order:

1. Command flags such as `--config`, `--profile`, `--base-url`, and `--api-key`
2. Environment variables `CONVERGE_BASE_URL` and `CONVERGE_API_KEY`
3. A discovered config file:
   - `.converge.toml` in the current working directory
   - `~/.config/converge/config.toml`

Use flags for one-off overrides. Use config files and profiles for stable defaults that should be reused by people or agents.

## Example

```toml
version = 1
base_url = "http://localhost:8080"
profile = "agent"

[defaults]
models = ["gpt-5-mini", "claude-sonnet-4"]
synth_model = "gpt-5-mini"
include_synthesis = true
wait = true
progress = "auto"
poll_interval = "2s"
timeout = "30m"

[profiles.agent]
models = ["gpt-5-mini", "claude-sonnet-4"]
synth_model = "gpt-5-mini"

[profiles.agent_quiet]
extends = "agent"
progress = "never"
```

## Notes

- Storing `api_key` in the config file is supported, but environment variables are safer when the workspace is shared.
- `--model` flags on `converge pulse run` override configured `models`.
- `--synth-model` overrides the configured `synth_model`.
- `--quiet` forces progress off even if the profile sets `progress = "auto"` or `"always"`.
