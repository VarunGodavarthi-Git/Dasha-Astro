param(
  [Parameter(Mandatory = $true)]
  [ValidateSet("dev", "build", "start", "lint")]
  [string]$Command
)

$ErrorActionPreference = "Stop"

$candidate = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
if (Test-Path -LiteralPath $candidate) {
  $node = $candidate
} else {
  $node = "node"
}

& $node ".\node_modules\next\dist\bin\next" $Command
exit $LASTEXITCODE
