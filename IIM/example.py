import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, Eq, solve

# For the thesis
# from sympy import symbols, Eq, solve
#
# # Define the variables
# theta_0, theta_1, lambda_ = symbols('theta_0 theta_1 lambda_')
#
# # Differentiate J with respect to theta_0 and theta_1
# partial_J_theta0 = 2*(theta_0 + theta_1 - 2) + 2*(theta_0 + 2.5*theta_1 - 3) + 2*lambda_*theta_0
# partial_J_theta1 = 2*(theta_0 + theta_1 - 2) + 5*(theta_0 + 2.5*theta_1 - 3) + 2*lambda_*theta_1
#
# # Set the derivatives to zero and solve for theta_0 and theta_1
# equation1 = Eq(partial_J_theta0, 0)
# equation2 = Eq(partial_J_theta1, 0)
#
# # The solutions will be in terms of lambda
# solutions = solve((equation1, equation2), (theta_0, theta_1))
# solutions


# For presentation:

# Data
Tids = ["t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "tx"]
A1 = [0, 0.8, 1.9, 2.9, 6.8, 7.5, 8.2, 9, 5]
A2 = [5.8, 4.6, 3.8, 3.2, 3, 4.1, 4.8, 5.5, None]

# Plotting
plt.figure(figsize=(10, 6), dpi=500)
plt.scatter(A1[:-1], A2[:-1], color="grey", edgecolors="black", s=100, zorder=3)
plt.axvline(x=A1[-1], color="black", linestyle="--", zorder=2)
for i, txt in enumerate(Tids[:-1]):
    plt.annotate(txt, (A1[i], A2[i]), fontsize=15, ha='left', va='bottom', zorder=30)
plt.annotate(Tids[-1], (A1[-1], 5.8), fontsize=15, ha='left', va='bottom', zorder=30)

# Increase the size of the x and y-axis labels
plt.xlabel("A1", fontsize=15)
plt.ylabel("A2", fontsize=15)

# Increase the size of the x and y-axis ticks
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

# plt.title("Plot of points with Tid labels", fontsize=16)
plt.xlim(0, 10)  # x range from 0 to 10
plt.ylim(-0.5, 7)  # y range from 0 to 7
plt.grid(False)


plt.savefig("figures/iim-1.png")

# Red Linear Regression for t1 to t4
x1 = A1[:4]
y1 = A2[:4]
slope1, intercept1 = np.polyfit(x1, y1, 1)  # 1 denotes linear regression

# Blue Linear Regression for t5 to t8
x2 = A1[4:8]
y2 = A2[4:8]
slope2, intercept2 = np.polyfit(x2, y2, 1)

# Find the intersection point x-coordinate
intersection_x = (intercept2 - intercept1) / (slope1 - slope2)

# Determine the boundaries of the x-coordinates for plotting
x1_reg = np.linspace(min(x1) - 0.5, intersection_x + 0.5, 100)
y1_reg = slope1 * x1_reg + intercept1
plt.plot(x1_reg, y1_reg, color="red", label="t1 to t4 regression", linewidth=2)

x2_reg = np.linspace(intersection_x - 0.5, max(x2) + 1, 100)
y2_reg = slope2 * x2_reg + intercept2
plt.plot(x2_reg+0, y2_reg, color="blue", label="t5 to t8 regression", linewidth=2)

# Legend to distinguish regression lines
# plt.legend(loc="best")

# plt.show()
plt.savefig("figures/iim-2.png")

# Compute the y-coordinate of the intersection using either of the regression equations
intersection_y = slope1 * intersection_x + intercept1

# Plot the intersection point
plt.scatter(intersection_x-0.05, intersection_y, color="black", edgecolors="black", s=150, zorder=4, label="Imputed")
plt.annotate('Imputed', (intersection_x-0.225, intersection_y+0.1), fontsize=14, ha='right', va='bottom', zorder=40)

# Save the figure
plt.savefig("figures/iim-3.png")