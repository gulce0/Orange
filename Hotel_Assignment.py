import PySimpleGUI as sg
import sqlite3
from datetime import datetime, timedelta


def show_add_hotel():
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    cur.execute("SELECT tid, tname, stdate, endate FROM Tour")
    tours = cur.fetchall()

    cur.execute("SELECT hid, city, brand FROM Hotel")
    hotels = cur.fetchall()
    con.close()

    layout = [
        [sg.Text("Assign Hotels for Tours", font=('Helvetica', 16), background_color='navyblue', text_color='white')],
        [sg.Text("Select a Tour", font=('Helvetica', 12), background_color='navyblue', text_color='white')],
        [sg.Listbox(tours, size=(50, 5), key="selected_tour", select_mode="single", background_color='white', text_color='black')],
        [sg.Text("Starting Date", font=('Helvetica', 12), background_color='navyblue', text_color='white'),
         sg.Input(key="stdate", background_color='white', text_color='black'),
         sg.CalendarButton("Pick Start Date", target="stdate", format="%Y-%m-%d", button_color=('white', 'navyblue'))],
        [sg.Text("Ending Date", font=('Helvetica', 12), background_color='navyblue', text_color='white'),
         sg.Input(key="endate", background_color='white', text_color='black'),
         sg.CalendarButton("Pick End Date", target="endate", format="%Y-%m-%d", button_color=('white', 'navyblue'))],
        [sg.Text("Filter by City", font=('Helvetica', 12), background_color='navyblue', text_color='white')],
        [sg.Combo(["All"] + list(set(hotel[1] for hotel in hotels)), key="city_filter", default_value="All", enable_events=True,
                  background_color='white', text_color='black')],
        [sg.Text("Available Hotels", font=('Helvetica', 12), background_color='navyblue', text_color='white')],
        [sg.Listbox(hotels, size=(50, len(hotels)), key="hotel_list", select_mode="single", background_color='white', text_color='black')],
        [sg.Button("Assign Hotel", button_color=('white', 'navyblue')), sg.Button("Close", button_color=('white', 'navyblue'))]
    ]

    window = sg.Window("Hotel Assignment", layout)

    def filter_hotels(hotels, city_filter):
        if city_filter == "All":
            return hotels
        return [hotel for hotel in hotels if hotel[1] == city_filter]

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Close"):
            break

        # Filter hotels by city
        if event == "city_filter":
            filtered_hotels = filter_hotels(hotels, values["city_filter"])
            window["hotel_list"].update(filtered_hotels)

        # Assign a hotel to a tour
        if event == "Assign Hotel":
            selected_tour = values["selected_tour"]
            selected_start_date = values["stdate"]
            selected_end_date = values["endate"]
            selected_hotel = values["hotel_list"]

            if not selected_tour:
                sg.popup("Please select a tour.", font=('Helvetica', 14))
                continue

            if not selected_start_date or not selected_end_date:
                sg.popup("Please select both start and end dates.", font=('Helvetica', 14))
                continue

            if not selected_hotel:
                sg.popup("Please select a hotel.", font=('Helvetica', 14))
                continue

            # Dates should be matching with the tour dates
            if selected_start_date < tour_start_date or selected_end_date > tour_end_date:
                sg.popup("Selected dates must be matching with the tour dates.", font=('Helvetica', 14))
                continue

            try:
                con = sqlite3.connect('Project.db')
                cur = con.cursor()

                # Check the availability of the hotel
                cur.execute("""
                    SELECT COUNT(*)
                    FROM reservation
                    WHERE hid = ? AND sdate <= ? AND edate >= ?
                """, (selected_hotel_id, selected_end_date, selected_start_date))
                if cur.fetchone()[0] > 0:
                    sg.popup("This hotel is already assigned for the selected dates.", font=('Helvetica', 14))
                    continue

                # Insert the hotel assignment into the reservation table
                cur.execute("""
                    INSERT INTO reservation (tid, hid, sdate, edate)
                    VALUES (?, ?, ?, ?)
                """, (tour_id, selected_hotel_id, selected_start_date, selected_end_date))
                con.commit()

                sg.popup("Hotel successfully assigned to the tour.", font=('Helvetica', 14))

            except Exception as e:
                sg.popup(f"Error occurred: {e}", font=('Helvetica', 14))
            finally:
                con.close()

    window.close()


if __name__ == "__main__":
    show_add_hotel()
