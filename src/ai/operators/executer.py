import subprocess

def execute_shell_command(command, command_args):
    argsCommand = []
    argsCommand.append(command)

    if command_args:
        argsCommand.extend(command_args.split(" "))
    
    print(argsCommand)
    try:
        result = subprocess.run(
            argsCommand, shell=False, text=True, capture_output=True
        )
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except Exception as e:
        return {"error": str(e)}

def process_command(llm_output):
    if llm_output.get("action") == "run_shell_command":
        command = llm_output.get("command")
        command_args = llm_output.get("command_args", "")
        if validate_command(command):
            return execute_shell_command(command, command_args)
        else:
            return {"error": "Command not allowed"}
    return {"error": "Unsupported action"}

def validate_command(command):
    ALLOWED_COMMANDS = ["ls", "du", "df", "whoami", "pwd"]
    command_name = command.split()[0]
    return command_name in ALLOWED_COMMANDS

