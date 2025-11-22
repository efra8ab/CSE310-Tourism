# important libraries 
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

#setting up our paths
data_path = Path(__file__).parent / "data" / "travel_items.csv"
metadata_path = Path(__file__).parent / "data" / "metadata_country.csv"
output_path = Path(__file__).parent/'outputs'


def main():

##### Step 1 - Loading the data and metadata
    raw_df = pd.read_csv(data_path, skiprows=4)
    meta_df = pd.read_csv(metadata_path, usecols=["Country Code", "Region"])

##### Step 2 - merging dataframes to use only real contries
    ## remove regions and keeping only real contries

    #using a merge on the left to keep all values from raw_df
    combined_df = raw_df.merge(meta_df, on="Country Code", how="left") 
    #filter for contries without a NA on the region column
    combined_df = combined_df[combined_df["Region"].notna()].copy()

##### Step 3 - check values on year columns

    #we first check all columns to see if the colum is a number (skipping strings)
    year_cols = [col for col in combined_df.columns if col.isdigit()]
    #then we subsitute all values on these columns to ensure they all are numbers
    #or placing a NaN in case there is an issue
    combined_df[year_cols] = combined_df[year_cols].apply(pd.to_numeric, errors='coerce')

##### Step 4 - Finding the latest year that actually has data

    last_year = None
    #review each column from latest to oldest
    for year in sorted(year_cols, reverse=True):
        #check if the column doesn't have any empty values (NaN)
        if combined_df[year].notna().any(): 
            last_year = year
            break
    if last_year is None:
        raise ValueError('Could not find any year columns with data')
    assert last_year is not None  # reassure type-checkers we found a year
    
##### Step 5 - Builing a table with the top five countries for the last available year
    top_countries = (
        #selecting the columns we will use
        combined_df[['Country Name', 'Country Code', last_year]]
        #dropping rows with NaN on the last year
        .dropna(subset=[last_year])
        #Sorting the values placing the largest on top
        .sort_values(last_year, ascending=False)
        #printing only the top 5
        .head(5)
        #change names for easier reading
        .rename(
            columns={
                'Country Name': 'Country',
                'Country Code': 'Code',
                last_year: f'{last_year}_Receipts_USD'
            }
        )
    )
    #changing format to add billions
    top_countries[f'{last_year}_Receipts_USD_Billions'] = (
        top_countries[f'{last_year}_Receipts_USD'] / 1e9
    ).round(2)

##### Step 6 - Building a table with global totals for the last 5 years

    #convert the last available year to int so we can count backwards
    last_year_int = int(last_year)
    #create a list with the last 5 years as strings (ex: ["2022","2021",...])
    recent_years = [str(last_year_int - i) for i in range(5)]
    #keep only the years that actually exist as columns in the dataframe
    recent_years = [year for year in recent_years if year in year_cols]

    #sum the receipts for all contries for each of these years
    global_totals = (
        combined_df[recent_years]
        .sum(skipna=True)           # sum by column (year)... ignoring NaN
        .reset_index()              # turn the Series into a DataFrame
        .rename(columns={'index': 'Year', 0: 'Receipts_USD'})
    )

    #make sure Year is numeric and add a billions column
    global_totals['Year'] = global_totals['Year'].astype(int)
    global_totals['Receipts_USD_Billions'] = (
        global_totals['Receipts_USD'] / 1e9
    ).round(2)

    #keep only the columns we care about and sort from oldest to newest year
    global_totals = global_totals[['Year', 'Receipts_USD_Billions']].sort_values('Year')


##### Step 6.5 - Quick charts for the outputs
    output_path.mkdir(exist_ok=True)

    fig, ax = plt.subplots()
    ax.bar(top_countries['Country'], top_countries[f'{last_year}_Receipts_USD_Billions'])
    ax.set_ylabel('USD billions')
    ax.set_title(f'Top tourism earners, {last_year}')
    plt.xticks(rotation=30, ha='right')
    fig.tight_layout()
    fig.savefig(output_path / f'top_countries_{last_year}.png', dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots()
    ax.plot(global_totals['Year'], global_totals['Receipts_USD_Billions'], marker='o')
    ax.set_ylabel('USD billions')
    ax.set_xlabel('Year')
    ax.set_title('Global tourism receipts (last 5 years with data)')
    fig.tight_layout()
    fig.savefig(output_path / 'global_receipts_recent_years.png', dpi=150)
    plt.close(fig)

##### Step 7 - wrap up 
    ##saving our tables into CSV files
    top_countries.to_csv(output_path / f'top_countries_{last_year}.csv', index=False)
    global_totals.to_csv(output_path / 'global_receipts_recent_years.csv', index=False)
    print('Tables saved to output folder')
    
    ##we can now view the top 5 earners on the last available year
    print("\nTop tourism earners (USD billions):")
    print(top_countries[['Country', 'Code', f'{last_year}_Receipts_USD_Billions']].to_string(index=False))
    ##we can also see total global receipts on USD billions
    print("\nGlobal tourism receipts (USD billions):")
    print(global_totals.to_string(index=False))

if __name__ == "__main__":
    main()
