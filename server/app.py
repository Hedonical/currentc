from shiny import App, render, ui, reactive
import flag
from country_dict import countries
from exchange_rate import scrape_currency_conversion
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from forex_python.converter import CurrencyCodes

c = CurrencyCodes()

all_countries = countries()

default_choices = {k: f"{flag.flag(v.code)} {v.name} {v.curr}" for (
    k, v) in all_countries.all.items() if "" in k}


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.div({"style": "font-weight: bold; margin-left: 2px;"},
               ui.input_numeric("am", "Amount", 1, min=0)),
        ui.div({"style": "font-weight: bold; margin-left: 2px;"},
               ui.input_text("z", "Filter", placeholder="Country Name"),
               ui.input_select("x", "Your Currency", default_choices, selected="United States")),
        ui.div({"style": "font-weight: bold; margin-left: 2px;"},
               ui.input_text("m", "Filter", placeholder="Country Name"),
               ui.input_select("y", "Convert to", default_choices, selected="Vietnam"))),
    ui.card(
        ui.div({"style": "text-align: center; background-color:#458f69; color:#FFFFFF"},
               ui.markdown("# Current¢")),
        ui.output_plot("historic")
    )

)


def server(input, output, session):

    @output
    @render.plot
    async def historic():

        # calculate the currency conversion
        output = await scrape_currency_conversion(all_countries.all[input.x()].curr,
                                                  all_countries.all[input.y(
                                                  )].curr,
                                                  input.am())

        output = output.sort_values(by='Date')

        fig, ax = plt.subplots()
        ax.plot(output["Date"], output["Price"])
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        plt.xticks(rotation=40)

        plt.xlabel('Date')
        plt.ylabel(c.get_symbol(all_countries.all[input.y(
        )].curr))  # NEED TO ADD CURRENCY SYMBOL

        plt.tight_layout()
        plt.show()
        return fig

    # update the Your currency input options based on text
    @reactive.Effect
    @reactive.event(input.z)
    def _():
        filter_str = input.z()
        if filter_str == "":
            return
        filtered_input = {k: f"{flag.flag(v.code)} {v.name} {v.curr}" for (
            k, v) in all_countries.all.items() if filter_str.lower() in k.lower()}

        ui.update_select(
            "x",
            choices=filtered_input,
        )

    @reactive.Effect
    @reactive.event(input.m)
    def _():
        filter_str = input.m()
        if filter_str == "":
            return

        filtered_input = {k: f"{flag.flag(v.code)} {v.name} {v.curr}" for (
            k, v) in all_countries.all.items() if filter_str.lower() in k.lower()}

        ui.update_select(
            "y",
            choices=filtered_input,
        )


app = App(app_ui, server, debug=True)
