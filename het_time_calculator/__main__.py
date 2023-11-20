import matplotlib.pyplot as plt

from .calculations import perform_all_calculations
from .config import HTC_CONFIG
from .plotting import plot_visit_histograms, setup_visit_plot


def main():
    """Main entry point for the application script"""
    target_table, visits_table = perform_all_calculations()
    HTC_CONFIG.write_output_file(target_table)

    fig, ax = setup_visit_plot()
    plot_visit_histograms(ax, visits_table)
    HTC_CONFIG.save_plot(fig)
    if HTC_CONFIG.show_plot:
        plt.show()


if __name__ == "__main__":
    main()
