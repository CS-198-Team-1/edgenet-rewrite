# Experiment recording

## General
### CSV tracking
By default, when an Experiment's `to_csv` method is called, it will save to `CSV_RESULTS_LOCATION` using the prescribed formats defined in `constants`. In the [Details](#details) section below, they will be recorded in order, separated by commas.

For example, for an Experiment, you should expect:
```csv
my_experiment_id,61325.21,2022...
```

The recording module will record a separate `.csv` file for Experiments, Jobs, and Sections and Looped Sections (both in one file).

## Structure
```
Experiment -> * Jobs -> Metrics -> * Sections and * Looped Sections
```
An Experiment can have many Jobs, and a Job has a single Metrics object attached to it, and a Metrics object can have many recorded Sections and Looped Sections.

## Details
### Experiment
- `experiment_id` - UUID of the particular Experiment
- `pipeline` - Pipeline used for the Experiment
- `total_elapsed_time` - Time taken for the Experiment from start to finish
- `start_time` - Time Experiment started (ISO format)
- `end_time` - Time Experiment ended (ISO format)

### Job
- `experiment_id` - Experiment ID the Job is associated with
- `job_id` - UUID of the particular Job
- `function_name` - Function name for the particular Job
- `total_elapsed_time` - Time taken for the Job from start to finish (taken from Metrics)
- `start_time` - Time Job started (ISO format)
- `end_time` - Time Job ended (ISO format)

### Sections and Looped Sections
- `job_id` - Job ID the Section is associated with
- `call_id` - UUID of the particular **function call**
- `section_id` - Name of the section timed
- `loop_index` - (For Looped Sections only) Index of the Looped Section in the list
- `total_elapsed_time` - Accurate elapsed time of whole section through `time.perf_counter()`