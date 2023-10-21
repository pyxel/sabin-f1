import csv
import duckdb
import streamlit as st
import pandas as pd


def get_data(f):
    with open(f, newline='') as csvfile:
        data = csv.reader(csvfile)
    return data


def load_tables():

    options = "(HEADER 1, DELIM ',')"
    data_dir = "data/"

    duckdb.sql(f"""
    CREATE OR REPLACE TABLE stake(player VARCHAR, driver VARCHAR, start_round INT, end_round INT, stake INT);
    COPY stake FROM '{data_dir}stake.csv' {options};""")

    duckdb.sql(f"""
    CREATE OR REPLACE TABLE contract(player VARCHAR, driver VARCHAR, start_round INT, end_round INT);
    COPY contract FROM '{data_dir}contract.csv' {options};""")

    duckdb.sql(f"""
    CREATE OR REPLACE TABLE driver(name VARCHAR, number VARCHAR, Nationality VARCHAR, DOB VARCHAR, driver VARCHAR);
    COPY driver FROM '{data_dir}driver.csv' (AUTO_DETECT true);""")

    duckdb.sql(f"""
    CREATE OR REPLACE TABLE result(round INT, type VARCHAR, position INT, driver VARCHAR, points INT);
    COPY result FROM '{data_dir}result.csv' {options};""")


def calculate_multipliers():
    sql = """
        create or replace table standing as
        with 
        driver_round as (
            select
                r.round,
                d.driver
            from driver d
            cross join (select distinct round from result) r
        )
        -- Aggregate the data by round (sum the sprint + race points)
        , round_result as (
            select
                d.round,
                d.driver,
                sum(ifnull(r.points, 0)) as points
            from driver_round d
            left join result r on r.driver = d.driver
                and r.round = d.round
            group by all
        )
        select
            round,
            driver,
            sum(points) over(
                partition by driver
                order by round
                rows between unbounded preceding and current row
            ) as points,
            sum(points) over(
                partition by driver
                order by round
                range between 4 preceding and current row
            ) as points_last5,
            points as points_this_round
        from round_result r
    """
    duckdb.sql(sql)
    #duckdb.sql("select * from standing where round = 18 and type = 'race' order by points desc").show()
    sql = """
        create or replace table multiplier as
        with normaliser as (
            select
                round,
                points + points_last5 as points_last5_plus_all
            from standing
            where driver = 'PER'
        )

        select
            s.driver,
            s.round + 1 as round,
            round(n.points_last5_plus_all / (s.points + s.points_last5), 2) as multiplier_raw,
            case
                when multiplier_raw > 50 then 50
                when multiplier_raw is null then 50
                else multiplier_raw
            end as multiplier
        from standing s
        join normaliser n on n.round = s.round
    """
    duckdb.sql(sql)

    sql = """
        create or replace table player_standing as
        with contract_multiplier as (
            select 
                c.*,
                ifnull(m.multiplier, 50) as multiplier
            from contract c
            left join multiplier m on m.driver = c.driver
                and m.round = c.start_round 
        )

        select 
            s.round,
            c.player,
            c.driver,
            s.points_this_round,
            c.multiplier,
            st.stake,
            round(s.points_this_round * c.multiplier * st.stake, 0) as player_points_this_round,
            sum(player_points_this_round) over(
                partition by c.player, c.driver
                order by s.round
                rows between unbounded preceding
                    and current row
            ) as player_points_total
        from standing s
        join contract_multiplier c on c.driver = s.driver
            and s.round between c.start_round and c.end_round
        join stake st on st.player = c.player
            and st.driver = c.driver
            and s.round between st.start_round and st.end_round
        order by 1, 3
    """
    duckdb.sql(sql)

    sql = """
        create or replace table round_player_standing as
        with round_player_standing as (
            select 
                round,
                player,
                sum(player_points_this_round) as player_points_this_round
            from player_standing
            group by all
            order by 1
        )
        , total as (
            select 
                *,
                sum(player_points_this_round) over(
                    partition by player
                    order by round
                    rows between unbounded preceding
                        and current row
                ) as player_points_total
            from round_player_standing
        )

        select *
        from total

    """
    duckdb.sql(sql)



def main():
    load_tables()
    calculate_multipliers()


if __name__ == '__main__':
    #main()
    pass

