import pandas as pd


def load_price_competitors():

    maxaro = pd.read_excel(
        "C:\\Users\\nick.sieraad\\Documents\\Projects\\scraping-concurrenten\\outputs\\maxaro.xlsx"
    )
    tegeldepot = pd.read_excel(
        "C:\\Users\\nick.sieraad\\Documents\\Projects\\scraping-concurrenten\\outputs\\tegeldepot.xlsx"
    )
    sanitairkamer = pd.read_excel(
        "C:\\Users\\nick.sieraad\\Documents\\Projects\\scraping-concurrenten\\outputs\\sanitairkamer.xlsx"
    )
    x2o = pd.read_excel(
        "C:\\Users\\nick.sieraad\\Documents\\Projects\\scraping-concurrenten\\outputs\\x2o.xlsx"
    )

    return maxaro, tegeldepot, sanitairkamer, x2o


def combine_competitors_today(maxaro, tegeldepot, sanitairkamer, x2o):

    price_swnl_pl_today = maxaro.merge(tegeldepot, on=["sku", "datum", "prijs_swnl", "levertijd_swnl"], how="outer")
    price_swnl_pl_today = price_swnl_pl_today.merge(sanitairkamer, on=["sku", "datum", "prijs_swnl", "levertijd_swnl"], how="outer")
    price_swnl_pl_today = price_swnl_pl_today.merge(x2o, on=["sku", "datum", "prijs_swnl", "levertijd_swnl"], how="outer")

    return price_swnl_pl_today


def calculate_delivery_in_days(price_swnl_pl_today):

    levertijd_days = []
    for levert in price_swnl_pl_today['levertijd_swnl']:
        if not pd.isna(levert):
            levert = levert.lower()
            if (levert == '24 hours delivery') or ('voor' in levert):
                levertijd_days.append(1)
            elif levert == '0 hours delivery':
                levertijd_days.append(0)
            elif ('days' in levert) or ('dag' in levert):
                levertijd_days.append([int(word) for word in levert.split() if word.isdigit()][0])
            elif ('week' in levert) or ('weken' in levert):
                levertijd_days.append([int(word) for word in levert.split() if word.isdigit()][0] * 7)
            elif levert.isdigit():
                levertijd_days.append(int(levert))
            else:
                levertijd_days.append('')
        else:
            levertijd_days.append('')

    price_swnl_pl_today['levertijd_days'] = levertijd_days

    return price_swnl_pl_today


def load_and_save_price_competitors(price_swnl_pl_today):

    price_swnl_pl_vs_price_competitors = pd.read_excel(
        "C:\\Users\\nick.sieraad\\Documents\\Projects\\scraping-concurrenten\\" +
        "outputs\\price_swnl_PL_vs_competitors.xlsx"
    )

    price_swnl_pl_vs_price_competitors = price_swnl_pl_vs_price_competitors.append(price_swnl_pl_today)
    price_swnl_pl_vs_price_competitors.to_excel(
        "C:\\Users\\nick.sieraad\\Documents\\Projects\\scraping-concurrenten\\" +
        "outputs\\price_swnl_PL_vs_competitors.xlsx", index=False
    )


def main():
    maxaro, tegeldepot, sanitairkamer, x2o = load_price_competitors()
    price_swnl_pl_today = combine_competitors_today(maxaro, tegeldepot, sanitairkamer, x2o)
    price_swnl_pl_today = calculate_delivery_in_days(price_swnl_pl_today)
    load_and_save_price_competitors(price_swnl_pl_today)


if __name__ == "__main__":
    main()
