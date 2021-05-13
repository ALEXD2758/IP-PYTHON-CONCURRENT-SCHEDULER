import asyncio
import json
import logging
import sys

# Global list of tasks already executed during the execution of the loop
tasks_list_executed = []


async def arguments_execution(task):
    # Define the list as global
    global tasks_list_executed

    # Check if the task name already exists in the global list
    if not task['name'] in tasks_list_executed:
        # Append the current task name if not present, to the global list of tasks executed
        tasks_list_executed.append(task['name'])
        log = logging.getLogger(f"{task['name']}".upper())
        # Set the task arguments inside the string variable
        code = task["arguments"]

        # Check if the task type is exec
        if task["type"].lower() == "exec":
            log.info('Started:')
            # Create a subprocess for executing a shell command
            proc = await asyncio.create_subprocess_shell(
                code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await proc.communicate()
            output = stdout.strip().decode('utf-8')
            # Check the output
            if not stdout and not stderr:
                log.info(f'No result')
                log.info('Ended:')
                return "OK"
            elif stderr and proc.returncode != 0:
                log.info('Ended:')
                return "FAILED"
            else:
                log.info(f'Result is : "{output}" ')
                log.info('Ended:')
                return "OK"

        # Check if the task type is eval
        elif task["type"].lower() == "eval":
            log.info('Started:')

            # Create a subprocess for executing a python code snippet
            try:
                proc = await asyncio.create_subprocess_exec(
                    'python', '-c', code,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE)
                stdout, stderr = await proc.communicate()
                proc.returncode
                output = stdout.strip().decode('utf-8')
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message)
                return "FAILED"
            # Check the output
            if not stdout and not stderr:
                log.info(f'No result')
                log.info('Ended:')
                return "OK"
            elif stderr and proc.returncode != 0:
                log.info('Ended:')
                return "FAILED"
            else:
                log.info(f'Result is : "{output}" ')
                log.info('Ended:')
                return "OK"


# Recursive function of a task as JSON Object, and the loaded JSON file
async def coro(task, loaded_data):
    # Check if dependencies exist in the task object
    if "dependencies" in task:
        # Defining the number of task dependencies present in the task itself
        count = len(task["dependencies"])
        # If 0 then execute the arguments present in the task
        if count == 0:
            task_execution = await arguments_execution(task)
            if task_execution == "FAILED":
                set_current_task_name(task)
                return "SKIPPED"
            else:
                set_current_task_name(task)
                return "OK"
        # If more than 0 dependencies in the task
        elif count > 0:
            # Iterate over each task dependency in the task
            for t in task["dependencies"]:
                # And for each dependency, iterate over each task object in the loaded file
                for task_value in loaded_data["tasks"]:
                    # If the task name corresponds, then relaunch this function with the task object found
                    if t.lower() == task_value['name'].lower():
                        await coro(task_value, loaded_data)
                        task_execution = await arguments_execution(task)
                        if task_execution == "FAILED":
                            set_current_task_name(task)
                            return "SKIPPED"
                        else:
                            set_current_task_name(task)
                            return "OK"
    # Execute the arguments present in task if "dependencies" doesn't exist in the task object
    else:
        task_execution = await arguments_execution(task)
        if task_execution == "FAILED":
            set_current_task_name(task)
            return "SKIPPED"
        else:
            set_current_task_name(task)
            return "OK"


def set_current_task_name(task):
    # Set the current Task name (understanding: "process") which differ from the task name in the loaded file
    asyncio.current_task().set_name(task["name"])


async def run_create_tasks():
    # Logging messages
    log = logging.getLogger('run_create_tasks')
    log.info('starting')

    # Open the Input file and load it inside a variable - Then close the file
    with open('data/input1.json') as file:
        loaded_data = json.load(file)
    file.close

    # Get the current event loop previously created
    loop = asyncio.get_event_loop()
    # List comprehension of create_task, in the current event loop, for all JSON objects
    # inside the array "tasks of the loaded file
    tasks = [loop.create_task(coro(i, loaded_data))
             for i in loaded_data["tasks"]]
    # Wait for asyncio to gather all values being returned from the coroutines
    await asyncio.gather(*tasks)
    # Wait for the tasks list
    await asyncio.wait(tasks)

    # Logging messages
    log.info('waiting for executor tasks')
    log.info('exiting')

    return tasks


if __name__ == '__main__':
    # Configure logging to show the Thread's name:
    logging.basicConfig(
        level=logging.INFO,
        format='%(threadName)10s %(name)18s: %(message)s',
        stream=sys.stderr,
    )

    # Create an asyncio event loop
    event_loop = asyncio.get_event_loop()
    try:
        report_status = event_loop.run_until_complete(
            run_create_tasks()
        )
    finally:

        # Print the TASKS REPORT with each element inside it
        print("TASKS REPORT:")
        print(*report_status, sep='\n')
        event_loop.close()
