# Zed Integration Research - What We Should Have Known

## The Truth About Zed + ACP

### ✅ Zed DOES Support ACP
From official docs: https://zed.dev/docs/extensions/agent-servers

**Key Finding**: 
> "Agent Server Extensions let you package up an Agent Server so that users can install the extension and have your agent easily available to use in Zed."

### What We Got Wrong

1. **Wrong Extension Type**: We tried to register as a `language_server`
2. **Should Be**: Register as an `agent_server` in extension.toml

### Correct Extension Format

```toml
# extension.toml
id = "lettabridge"
name = "Letta Bridge"
description = "Connect to Letta agents with persistent memory"
version = "0.1.0"
schema_version = 1
authors = ["Jonny Dubowsky"]
repository = "https://github.com/jonnydubowsky/lettabridge"

[agent_servers.lettabridge]
name = "Letta Agent"

# Platform-specific configuration
[[agent_servers.lettabridge.targets]]
os = "macos"
arch = "aarch64"
archive = "https://github.com/jonnydubowsky/lettabridge/releases/download/v0.1.0/lettabridge-macos-aarch64.tar.gz"
cmd = "acp_letta_bridge.py"
sha256 = "..."

# Environment variables
[agent_servers.lettabridge.env]
BRIDGE_LETTA_BASE_URL = "https://api.letta.com"
```

### How It Actually Works

1. User installs extension from Zed marketplace or as dev extension
2. Extension provides agent through ACP protocol
3. User activates agent in Zed's agent panel (Cmd+Shift+A)
4. Zed spawns the agent process and communicates via stdin/stdout

### What We Built (Status)

✅ **Correct**: ACP bridge implementation (acp_letta_bridge.py)
✅ **Correct**: JSON-RPC over stdio protocol
✅ **Correct**: Letta Cloud integration
❌ **Wrong**: Extension packaging format
❌ **Missing**: Binary distribution (needs PyInstaller)
❌ **Missing**: Proper extension.toml format

## Next Steps (The Right Way)

1. **Fix extension.toml** to use agent_servers format
2. **Build binary** with PyInstaller for distribution
3. **Test as dev extension** using: `zed: install dev extension`
4. **Verify** agent appears in agent panel
5. **Only then** work on publishing

## Lessons Learned

This should have been Step 1, not discovered after building the entire bridge.

**Always start with:**
- Official docs: https://zed.dev/docs/extensions/agent-servers
- Working examples from extension marketplace
- Minimal test extension before full implementation
