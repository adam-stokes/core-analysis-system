#  init
#  initialization file
#  Copyright (C) 2010 Adam Stokes
#  
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#   
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#   
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

error_messages = {
    # Timestamp
    1 : "Could not parse timestamp",
    2 : "Could not match timestamp",
    # Cores
    3 : "Could not extract core",
    4 : "Could not capture timestamp",
    5 : "Could not guess extraction format",
    6 : "Could not determine if file is proper vmcore",
    7 : "Error opening file",
    8 : "Could not compress core",
    # Jobs
    40 : "Could not find existing job",
    # Servers
    80 : "No suitable servers found",
    # Misc
    100 : "This needs root access to run.",
    }


info_messages = {
    1 : "Building directory structure",
    2 : "Starting job",
    3 : "Processing corefile",
    4 : "Job complete",
    5 : "Matched timestamp",
}
