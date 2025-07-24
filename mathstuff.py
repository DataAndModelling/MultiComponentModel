import math

def gamma_approx(x):
    if x <= 0:
        raise ValueError("Gamma function is not defined for non-positive values.")
    approx = math.sqrt(2 * math.pi / x) * (x / math.e) ** x
    return approx


def weibull_mean(k, lambd):
    if k <= 0:
        raise ValueError("Shape parameter k must be positive.")

    # Calculate the mean using the formula: lambda * Gamma(1 + 1/k)
    gamma_term = gamma_approx(1 + 1 / k)
    return lambd * gamma_term
