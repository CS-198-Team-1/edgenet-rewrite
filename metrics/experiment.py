import datetime, uuid, csv
from .constants import CSV_FORMAT_EXPERIMENT, CSV_FORMAT_JOBS, CSV_FORMAT_SECTIONS, CSV_RESULTS_LOCATION


class Experiment:
    """
    A class that holds experiment details for multiple jobs, to be run in a pipeline (preferably in the cloud)
    """
    def __init__(self, pipeline, experiment_id=None):
        self.experiment_id = experiment_id or str(uuid.uuid4())
        self.jobs = []
        self.start_time = datetime.datetime.now()
        self.end_time = None
        self.pipeline = pipeline

    def end_experiment(self):
        self.end_time = datetime.datetime.now()

    @property
    def elapsed(self): return (self.end_time - self.start_time).total_seconds()

    def to_csv(self, results_location=CSV_RESULTS_LOCATION):
        # Store experiment data:
        data = [(
            self.experiment_id, self.elapsed, self.pipeline,
            self.start_time.isoformat(), self.end_time.isoformat()
        )]

        self.csv_write(data, results_location, CSV_FORMAT_EXPERIMENT)

        # Store jobs data:
        jobs_data = []
        metrics_data = []
        for job in self.jobs:
            metrics = job.metrics
            ft = metrics.function_time
            data = (
                self.experiment_id, job.job_id, job.function_name,
                ft.elapsed, metrics.function_started.isoformat(), metrics.function_ended.isoformat()
            )
            jobs_data.append(data)

            for name, section in metrics.sections.items():
                data = (
                    job.job_id, metrics.call_id, name, None,
                    section.elapsed
                )
                metrics_data.append(data)

            for name, section_list in metrics.looped_sections.items():
                for i, section in enumerate(section_list):
                    data = (
                        job.job_id, metrics.call_id, name, i,
                        section.elapsed
                    )
                    metrics_data.append(data)

        self.csv_write(jobs_data, results_location, CSV_FORMAT_JOBS)
        self.csv_write(metrics_data, results_location, CSV_FORMAT_SECTIONS)

    def csv_write(self, data, results_location, file_suffix):
        with open(f"{results_location}{self.experiment_id}{file_suffix}", "a+") as fp:
            writer = csv.writer(fp, delimiter=",")
            writer.writerows(data)
        

