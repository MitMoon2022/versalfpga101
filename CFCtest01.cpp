#include <iostream>
#include <string>
#include <ctime>

using namespace std;

int countContinuousFailuresOf3() {
    int count = 0;
    int consecutiveFailures = 0;
    string input;

    cout << "Enter strings (enter 'br' to stop):\n";

    while (cin >> input) {
        time_t now = time(0); // Update the current time inside the loop

        if (input == "br") {
            break; // Stop input if 'br' is entered
        }

        try {
            int num = stoi(input);
            if (num == 3) {
                consecutiveFailures++;
                cout << "Cons_Fail is now: " << consecutiveFailures << endl;
                if (consecutiveFailures == 3) {
                    count++;
                    cout << "CFC is: " << count << " time" << endl;
                    char* date_time = ctime(&now);
                    //Pls log down the date/time that it occured.
                    cout << "The current date and time is: " << date_time << endl;

                    consecutiveFailures = 0; // reset the count after reaching 3 consecutive failures
                    break;  //break-out!
                }
            } else {
                cout<<"Non-failure outcome!"<<endl;
                consecutiveFailures = 0; // reset the count if a non-failure element is encountered
            }
        } catch (const invalid_argument& e) {
            cerr << "Invalid input. Please enter integers or 'br' to stop.\n";
        }
    }

    return count;
}

int main() {

    cout<<"The program is to demonstrate the continuous failure count works."<<endl;
    cout<<"Enter '3' for a fail outcome."<<endl;
    int result = countContinuousFailuresOf3();

    cout << "Hit CFC - Alarm Err code -1234!: " << result << endl;

    return 0;
}
