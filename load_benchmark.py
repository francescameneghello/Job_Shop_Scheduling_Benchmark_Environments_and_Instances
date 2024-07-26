
from solution_methods.helper_functions import load_parameters, load_job_shop_env
from solution_methods.cp_sat import JSPmodel
from solution_methods.cp_sat.utils import solve_model
import json

problem_instance = "/jsp/demirkol/cscmax_20_15_1.txt"
time_limit = 10

jobShopEnv = load_job_shop_env(problem_instance)
model, vars = JSPmodel.jsp_cp_sat_model(jobShopEnv)
solver, status, solution_count, solutions = solve_model(model, time_limit, vars, jobShopEnv)
jobShopEnv, output = JSPmodel.update_env(jobShopEnv, vars, solver, status, solution_count, time_limit)

parameters_sim = {"start_timestamp":  "2023-08-22 7:45:00", "jobs": {}, "machines": [str(i) for i in range(jobShopEnv.nr_of_machines)],
                  "name_beanchmark": problem_instance}

for idx, job in enumerate(jobShopEnv.jobs):
    machine_seq = []
    times = []
    for operation in job.operations:
        for k, v in operation.processing_times.items():
            machine_seq.append(str(k))
            times.append(operation.simulation_parameters)

    parameters_sim['jobs'][idx] = {"machine_seq": machine_seq, "times": times}

parameters_sim['solutions'] = solutions
parameters_sim['n_solutions'] = len(solutions)


with open('simulation_settings.json', 'w') as outfile:
    json.dump(parameters_sim, outfile, indent=2)