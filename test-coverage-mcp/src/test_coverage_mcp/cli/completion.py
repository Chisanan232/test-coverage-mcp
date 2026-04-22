"""Shell completion support for CLI."""

import click


@click.command()
@click.option(
    "--shell",
    type=click.Choice(["bash", "zsh", "fish"]),
    required=True,
    help="Shell type for completion",
)
def completion(shell: str) -> None:
    """Generate shell completion script.

    Supports bash, zsh, and fish shells.
    """
    if shell == "bash":
        click.echo("""# Bash completion for test-coverage-mcp
_test_coverage_mcp_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    opts="serve providers doctor --help --verbose --config"

    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}
complete -o bashdefault -o default -o nospace -F _test_coverage_mcp_completion test-coverage-mcp
""")
    elif shell == "zsh":
        click.echo("""# Zsh completion for test-coverage-mcp
#compdef test-coverage-mcp

_test_coverage_mcp() {
    local -a commands
    commands=(
        'serve:Start the MCP server'
        'providers:Manage coverage providers'
        'doctor:Check environment and system health'
    )

    _describe 'command' commands
}

_test_coverage_mcp
""")
    elif shell == "fish":
        click.echo("""# Fish completion for test-coverage-mcp
complete -c test-coverage-mcp -f
complete -c test-coverage-mcp -n "__fish_use_subcommand_from_list serve providers doctor" -s h -l help -d "Show help"
complete -c test-coverage-mcp -n "__fish_use_subcommand_from_list serve providers doctor" -s v -l verbose -d "Enable verbose output"
complete -c test-coverage-mcp -f -n "__fish_use_subcommand_from_list" -a "serve" -d "Start the MCP server"
complete -c test-coverage-mcp -f -n "__fish_use_subcommand_from_list" -a "providers" -d "Manage coverage providers"
complete -c test-coverage-mcp -f -n "__fish_use_subcommand_from_list" -a "doctor" -d "Check environment and system health"
""")
