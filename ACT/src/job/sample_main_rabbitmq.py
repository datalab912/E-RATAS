import numpy as np
from simple_Rabbitmq import ACT

if __name__ == "__main__":
    # Create a sample P array
    P = np.array([[1, 2, 3],
                  [0, 0, 0],
                  [0, 0, 0]])

    # Create an instance of the ACT class with the sample array and an array_ID
    act_instance = ACT(P, "array_001")

    # Start the filling process
    act_instance.filling()
    print(P)
