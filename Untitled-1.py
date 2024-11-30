def show_add_transportation():
    

    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    # Get the transportation options from the database
    cur.execute("SELECT type, starting_point, destination FROM Transportation")
    transportation_options= cur.fetchall()

    # Get the tour code from the database
    cur.execute("SELECT MAX(tid) FROM Tour")
    result1 = cur.fetchone()
    tid = result1[0]

    # Get the starting and end dates of the tour
    cur.execute("SELECT stdate,endate FROM Tour WHERE tid = ?",  (tid,))
    result2 = cur.fetchone()
    stdate = result2[0]
    endate = result2[1]
    con.close()

    # Convert the start and end dates to datetime objects
    start_date_obj = datetime.strptime(stdate, '%Y-%m-%d')
    end_date_obj = datetime.strptime(endate, '%Y-%m-%d')

    # Generate a list of dates between start_date_obj and end_date_obj
    available_dates = []
    current_date = start_date_obj
    while current_date <= end_date_obj:
        available_dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    assigned_transportation = {date: None for date in available_dates}

    layout = [
        [sg.Text("Choose Transportation of Tour", font=('Helvetica', 16))],
        [sg.Text('Starting Date', background_color='navyblue', text_color='white'), sg.Input(key='stdate', size=(20, 1)), sg.CalendarButton("Choose Starting Date", target="stdate", format="%Y-%m-%d", default_date_m_d_y=(start_date_obj.month, start_date_obj.day, start_date_obj.year), close_when_date_chosen=True, begin_at_sunday_plus=1)],
        [sg.Text('Ending Date', background_color='navyblue', text_color='white'), sg.Input(key='endate', size=(20, 1)), sg.CalendarButton("Choose Ending Date", target="endate", format="%Y-%m-%d", close_when_date_chosen=True, begin_at_sunday_plus=1)],
        [sg.Combo(["All", "Plane", "Train", "Boat", "Bus"], key="t_filter", default_value="All", enable_events=True)],
        [sg.Text("Filter by starting point", font=('Helvetica', 16))],
        [sg.Combo(["All", "Istanbul", "Moscow", "Berlin", "Athens", "New York", "Tokyo", "London", "Madrid", "Naples", "Los Angeles", "Dubai", "Zurich", "Helsinki", "Tallinn", "Bangkok", "Munich", "Brussels", "Sydney", "Warsaw", "Oslo"], key= "s_filter", default_value="All", enable_events=True)],
        [sg.Text("Filter by destination", font=('Helvetica', 16))],
        [sg.Combo(["All",'Rome', 'Paris', 'Prague', 'Santorini', 'Boston', 'Seoul', 'Edinburgh', 'Barcelona', 'Palermo', 'San Francisco', 'Cairo', 'Geneva', 'Stockholm', 'Helsinki', 'Singapore', 'Vienna', 'Amsterdam', 'Melbourne', 'Krakow', 'Copenhagen'], key= "d_filter", default_value="All", enable_events=True)],
        [sg.Text("Available Transportation Options", font=('Helvetica', 16))],
        [sg.Listbox(transportation_options, key="transportation_options", size=(30, len(transportation_options)), select_mode='single', enable_events=True)],
        [sg.Button("Assign Transportation", font=('Helvetica', 16))],
        [sg.Button("Close", font=('Helvetica', 16))]]
        
    layout = [[sg.Column(layout, scrollable=True, vertical_scroll_only=True, size=(600, 400))]]
    window = sg.Window('Transportation_Page', layout)

    def filter_transportation(options, t_filter, s_filter, d_filter):
        filtered_options = []
        for option in options:
            if (t_filter == "All" or option[0] == t_filter) and \
               (s_filter == "All" or option[1] == s_filter) and \
               (d_filter == "All" or option[2] == d_filter):
                filtered_options.append(option)
        return filtered_options

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Close":
            break
        
        # Filter Process
        if event in ("t_filter", "s_filter", "d_filter"):
            filtered_options = filter_transportation(transportation_options, values["t_filter"], values["s_filter"], values["d_filter"])
            window["transportation_options"].update(filtered_options)

        # Date arrangements
        if event == "Assign Transportation":
            selected_start_date = values["stdate"]
            selected_end_date = values["endate"]
            t_transportation = values['transportation_options']
            
            if not selected_start_date or not selected_end_date:
                sg.popup("Please select both start and end dates.", font=('Helvetica', 14))
                continue
            
            if selected_start_date not in available_dates or selected_end_date not in available_dates:
                sg.popup("Selected dates must be within the available dates range.", font=('Helvetica', 14))
                continue
            
            if selected_end_date < selected_start_date:
                sg.popup("End date cannot be earlier than start date.", font=('Helvetica', 14))
                continue
            
            if not t_transportation or len(t_transportation[0]) < 3:
                sg.popup("Please select a valid transportation option.", font=('Helvetica', 14))
                continue
            
            try:
                print("Starting choose tour options", flush=True)
                t_type = t_transportation[0][0]
                t_start = t_transportation[0][1]
                t_destination = t_transportation[0][2]

                print(f"Inserting: {t_type}, {t_start}, {t_destination}", flush=True)
                con = sqlite3.connect('Project.db')
                cur = con.cursor()
                

                # Fetch the tcode from the Transportation table
                cur.execute("SELECT tcode FROM Transportation WHERE type = ? AND starting_point = ? AND destination = ?", (t_type, t_start, t_destination))
                result = cur.fetchone()
                if result is None:
                    sg.popup("Transportation option not found in the database.", font=('Helvetica', 14))
                    continue
                t_code = result[0]

                                # Check for existing assignments for the selected dates
                cur.execute("SELECT COUNT(*) FROM Assign WHERE sdate <= ? AND edate >= ? AND tid = ?", (selected_end_date, selected_start_date, tid))
                result = cur.fetchone()
                if result[0] > 0:
                    sg.popup("Transportation already assigned for the selected dates.", font=('Helvetica', 14))
                    continue

                # Ensure dates are in the correct format
                try:
                    selected_start_date = datetime.strptime(selected_start_date, '%Y-%m-%d').strftime('%Y-%m-%d')
                    selected_end_date = datetime.strptime(selected_end_date, '%Y-%m-%d').strftime('%Y-%m-%d')
                except ValueError:
                    sg.popup("Invalid date format. Please use YYYY-MM-DD.", font=('Helvetica', 14))
                    continue

                # Insert the new assignment
                cur.execute("INSERT INTO Assign (tid, tcode, sdate, edate) VALUES (?, ?, ?, ?)",
                            (tid, t_code, selected_start_date, selected_end_date))
                con.commit()
                print("Insert committed successfully", flush=True)
                sg.popup('Transportation created successfully', font=('Helvetica', 14))

                # Check if all dates have transportation assigned
                cur.execute("SELECT sdate, edate FROM Assign WHERE tid = ?", (tid,))
                assigned_dates = cur.fetchall()
                assigned_dates_set = set()
                for sdate, edate in assigned_dates:
                    current_date = datetime.strptime(sdate, '%Y-%m-%d')
                    end_date = datetime.strptime(edate, '%Y-%m-%d')
                    while current_date <= end_date:
                        assigned_dates_set.add(current_date.strftime('%Y-%m-%d'))
                        current_date += timedelta(days=1)

                unassigned_dates = set(available_dates) - assigned_dates_set
                if not unassigned_dates:
                    sg.popup("All dates have transportation assigned.", font=('Helvetica', 14))
                    window.close()
                else:
                    unassigned_dates_list = list(unassigned_dates)
                    unassigned_dates_list.sort()
                    sg.popup(f"Some dates are still unassigned: {', '.join(unassigned_dates_list)}", font=('Helvetica', 14))
                    available_dates = unassigned_dates_list
                    assigned_transportation = {date: None for date in available_dates}
                    window["stdate"].update("")
                    window["endate"].update("")
                    window["transportation_options"].update(filtered_options)
            except Exception as e:
                print(f"Error occurred: {e}", flush=True)
            finally:
                con.close()
                print("Database connection closed", flush=True)

    window.close()