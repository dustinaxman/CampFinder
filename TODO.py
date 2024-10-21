/Users/deaxman/Downloads/recgov_all_converted_100824.jsonl



make campsite to campground map and reverse


add in AVAILABLE filter given date spec (they give the date spec and WE pass list of campgrounds/sites and it filters to only return the available ones)

make the project repo
add to github (check for keys)
add docker
test grabbing with curl




given campsite/campground list, register for them for a date, with an email (utils.py)






# check if the llm works to get info (how to format, structured out)
# add in the dynamic grabbing of info about the stuff nearby

# look at camply and figure out how it works
# host it so I can provide list of campsites or campground and date and get a list of ones available on that date
# OR
# give a date and an email and a set of campgrounds/sites and message them when one is open
# get to the point where we have an api that 
#     1. gives a set of campsites or campground (based on a bunch of filter inputs and text with model, etc)
#     2. the ability to see only available or both and select to be notified






IDEA: random sample stats from campsite attrs etc and then use llm to make statement in text requesting campsite with those things 
add all of the possibilities to structured output for searching




python3.9 convert_and_process_raw_data.py /Users/deaxman/Downloads/all_recdatapull_files/all_data_backup2_GOOD_1188.jsonl /Users/deaxman/Downloads/recgov_all_converted_100824.jsonl /Users/deaxman/Downloads/recgov_camp_id_maps_100824.json