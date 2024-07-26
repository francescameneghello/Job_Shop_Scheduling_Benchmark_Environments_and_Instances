from ortools.sat.python import cp_model
import collections

class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solution_methods."""

    def __init__(self, vars, jobShopEnv):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__solution_count = 0
        self.__vars = vars
        self.__jobShopEnv = jobShopEnv
        self.__solutions = {}

    def on_solution_callback(self):
        """Called at each new solution."""
        print(
            "Solution %i, time = %f s, objective = %i"
            % (self.__solution_count, self.WallTime(), self.ObjectiveValue())
        )
        all_tasks = self.__vars['all_tasks']
        jobs_data = [[(k, v) for operation in job.operations for k, v in operation.processing_times.items()] for job in
                     self.__jobShopEnv.jobs]

        assigned_jobs = collections.defaultdict(list)
        assigned_task_type = collections.namedtuple(
            "assigned_task_type", "start job index duration"
        )
        for job_id, job in enumerate(jobs_data):
            for task_id, task in enumerate(job):
                machine = task[0]
                assigned_jobs[machine].append(
                    assigned_task_type(
                        start=self.Value(all_tasks[job_id, task_id].start),
                        job=job_id,
                        index=task_id,
                        duration=task[1],
                    )
                )

        num_machines = self.__jobShopEnv.nr_of_machines
        all_machines = range(num_machines)
        schedule_simulation = {}
        for machine in all_machines:
            assigned_jobs[machine].sort()
            schedule_simulation[str(machine)] = []
            for assigned_task in assigned_jobs[machine]:
                schedule_simulation[str(machine)].append(str(assigned_task.job))

        print('################################ Schedule solution ', self.__solution_count)
        self.__solutions[self.__solution_count] = {'makespan': self.ObjectiveValue(), 'solution': schedule_simulation}
        print(self.__solutions[self.__solution_count])
        self.__solution_count += 1

    def solution_count(self):
        return self.__solution_count

    def solutions(self):
        return self.__solutions


def  solve_model(
    model: cp_model.CpModel, time_limit: float | int, vars, jobShopEnv
) -> tuple[cp_model.CpSolver, int, int]:
    """
    Solves the given constraint programming model within the specified time limit.

    Args:
        model: The constraint programming model to solve.
        time_limit: The maximum time limit in seconds for solving the model.

    Returns:
        A tuple containing the solver object, the status of the solver, and the number of solution_methods found.
    """
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solution_printer = SolutionPrinter(vars, jobShopEnv)
    status = solver.Solve(model, solution_printer)
    solution_count = solution_printer.solution_count()
    solutions = solution_printer.solutions()
    return solver, status, solution_count, solutions
