import matplotlib.pyplot as plt

def embed_figure(fig, parent, toolbar=True, save_path=None):
    """Минимальный fallback через FigureCanvasTkAgg."""
    try:
        from matplotlib.backends.backend_tkagg import (
            FigureCanvasTkAgg, NavigationToolbar2Tk)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        if toolbar:
            tb = NavigationToolbar2Tk(canvas, parent, pack_toolbar=False)
            tb.update()
            tb.pack(side="bottom", fill="x")
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Добавляем возможность сохранения изображения
        if save_path:
            fig.savefig(save_path)
    except Exception:
        plt.show()
