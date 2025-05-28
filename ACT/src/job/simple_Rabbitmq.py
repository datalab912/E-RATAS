import pika
import json
import numpy as np

class ACT:
    def __init__(self, P, array_ID):
        self.P = P
        self.array_ID = array_ID
        self.queue_name = array_ID
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)
        self.pending_a_jobs = self.P.shape[1]  # Number of columns, thus number of A jobs

    def filling(self):
        # Publish jobs for each column to apply function A
        for x in range(self.P.shape[1]):
            job_id = f"{self.array_ID}+{x}"
            self.publish_job(job_id, 'A', {'column': x})

        # Start consuming the queue (which will eventually trigger the final B job)
        self.consume_queue()

    def publish_job(self, job_id, job_type, payload):
        job = {
            'job_id': job_id,
            'job_type': job_type,
            'payload': payload
        }
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue_name,
                                   body=json.dumps(job))
        print(f" [x] Sent {job_id}")

    def consume_queue(self):
        def callback(ch, method, properties, body):
            job = json.loads(body)
            job_id = job['job_id']
            job_type = job['job_type']
            payload = job['payload']

            if job_type == 'A':
                self.process_A(job_id, payload['column'])
                self.pending_a_jobs -= 1
                if self.pending_a_jobs == 0:
                    # Once all A jobs are done, publish the final B job
                    final_job_id = self.array_ID
                    self.publish_job(final_job_id, 'B', {})

            elif job_type == 'B':
                self.process_B()
                # Stop consuming after processing the final B job
                self.channel.stop_consuming()
                # Delete the queue after processing is complete
                self.channel.queue_delete(queue=self.queue_name)

            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()
        print(' [*] Processing finished.')

    def process_A(self, job_id, x):
        self.P[1, x] = A(self.P[0, x])
        print(f" [x] Processed {job_id} - A: P[1,{x}] = {self.P[1, x]}")

    def process_B(self):
        B(self.P)
        print(f" [x] Processed final job {self.array_ID} - B: P[2,:] = {self.P[2,:]}")

def A(value):
    return value * 100

def B(P):
    P[2, :] = P[0, :] + P[1, :]

if __name__ == "__main__":
    print("This is the ACT module.")
