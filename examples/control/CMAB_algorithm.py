import numpy as np
import GPy

class ContextualUCB:
    def __init__(self, n_radar_angle, n_beamforming_angle, kernel=None, delta=0.80):
        self.n_contexts = n_radar_angle
        self.n_actions = n_beamforming_angle
        self.delta = delta

        self.X = []  # List to store input data
        self.Y = []  # List to store output data

        # Initialize Gaussian Process Models for each radar angle
        if kernel is None:
            kernel = GPy.kern.RBF(input_dim=2, variance=1., lengthscale=1.)
        self.gp_models = [GPy.models.GPRegression(np.array([[0, 0]]), np.array([[0]]), kernel)
                          for _ in range(n_radar_angle)]

        self.beta = None  # Exploration-exploitation trade-off parameter

    def get_ucb_value(self, radar_angle):
        ucb_values = np.zeros(self.n_actions)
        for action in range(self.n_actions):
            mean, variance = self.gp_models[radar_angle].predict(np.array([[radar_angle, action]]))
            std = np.sqrt(variance)
            ucb_values[action] = mean.squeeze() + np.sqrt(self.beta) * std.squeeze()
        return ucb_values

    def angle_selection(self, radar_angle):
        ucb_value = self.get_ucb_value(radar_angle)
        return np.argmax(ucb_value) - 60  # Adjusting the angle range to (-60,60)

    def update(self, radar_angle, beamforming_angle, reward):
        new_X = np.array([[radar_angle, beamforming_angle]])
        new_Y = np.array([[reward]])

        self.X.append(new_X)
        self.Y.append(new_Y)

        self.gp_models[radar_angle].set_XY(np.vstack(self.X), np.vstack(self.Y))
        self.beta = self.optimal_beta_selection(len(self.X), self.delta)

    def optimal_beta_selection(self, t, delta):
        return 2 * np.log(self.n_actions * self.n_contexts * (t ** 2) * (np.pi ** 2) / (6 * delta))

    def save_trained_model(self, filename_X_csv, filename_Y_csv):
        # Correct the format of X and Y
        X_array = np.vstack(self.X)  # Ensure 2D array
        Y_array = np.vstack(self.Y)  # Ensure 2D array

        # Saving X and Y in CSV format
        np.savetxt(filename_X_csv, X_array, delimiter=',', fmt='%f')
        np.savetxt(filename_Y_csv, Y_array, delimiter=',', fmt='%f')

    def load_trained_model(self, filename_X_csv, filename_Y_csv):
        # Loading X and Y from CSV
        X_array = np.loadtxt(filename_X_csv, delimiter=',',ndmin=2)
        Y_array = np.loadtxt(filename_Y_csv, delimiter=',',ndmin=2)

        self.X = X_array.tolist()
        self.Y = Y_array.tolist()

        # Retrain the model for each radar angle
        for radar_angle in range(self.n_contexts):
            if self.X and self.Y:  # Ensure lists are not empty
                X_train = np.array(self.X)
                y_train = np.array(self.Y)
                self.gp_models[radar_angle].set_XY(X_train, y_train)
                self.gp_models[radar_angle].optimize()

    def save_mean_variance(self, filename_mean_csv, filename_variance_csv):
        means = []
        variances = []

        for radar_angle in range(self.n_contexts):
            for action in range(self.n_actions):
                mean, variance = self.gp_models[radar_angle].predict(np.array([[radar_angle, action]]))
                means.append([radar_angle, action, mean.item()])
                variances.append([radar_angle, action, variance.item()])

        # Convert to NumPy array and save
        np.savetxt(filename_mean_csv, np.array(means), delimiter=',', fmt='%f')
        np.savetxt(filename_variance_csv, np.array(variances), delimiter=',', fmt='%f')



# Example usage:
#contextual_gp_ucb = ContextualUCB(n_radar_angle=181, n_beamforming_angle=121)
# For actual use, call update, angle_selection, etc. here

# Saving and loading the model
#contextual_gp_ucb.save_trained_model('X_data.csv', 'Y_data.csv')
#contextual_gp_ucb.load_trained_model('X_data.csv', 'Y_data.csv')

# Save mean and variance
#contextual_gp_ucb.save_mean_variance('mean_data.csv', 'variance_data.csv')

