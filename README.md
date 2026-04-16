CSCB20 - Project Report: D&B UTSC Marketplace

University of Toronto Scarborough
Team: DB Master
Jiayi Zhang 
Ziruo Wang 
April 16 2026
 
Project overview
D&B UTSC Marketplace is a dedicated peer-to-peer e-commerce web application for the University of Toronto Scarborough (UTSC) community. Unlike traditional platforms, our system does not require online transactions. Instead, once a student expresses interest in an item, both parties can communicate directly to negotiate prices and arrange exchanges. Since all users are part of the UTSC community, this approach enhances both convenience and trust while creating a safer, more personalized trading environment.

It allows users to:
•	Browse items by category
•	Search for specific products
•	Filter results by price, condition, and popularity
•	Like and save interesting items
•	Post their own items for sale
•	Manage their profile and listings
The core idea is to create a campus-focused marketplace where students can safely and efficiently exchange goods they need.

System description
1.	Unified navigation: Every page shares a consistent header with a welcome message, search bar, like counter shortcut, profile access, and login/logout controls.
2.	Dynamic homepage: Displays three curated sections: New Arrivals, Featured Items (most popular), and Exam Essentials (items priced $10–$50 in the Stationery category).
3.	Category browsing: Users can explore items across 17 predefined categories, including Automotive, Clothing, Footwear, Furniture, Electronics, and Stationery.
4.	Advanced filtering: Within a category, users can filter by keyword, price range, item condition (Brand New, Like New, Minor Scratches, Visible Scratches, Poor Condition), and sort by price (low-to-high or high-to-low), most liked, or most recent.
5.	Item details: Each item page shows the product image, name, price, category, condition, full specifications, and current like count. Users can click a heart button to "like" an item (one like per user per item).
6.	Liked items: Users can view their 5 most recently liked items or see all liked items on a dedicated page.
7.	Profile management: Users see their name, email address (which is intentionally visible to buyers for contact purposes), and a preview of their own posted listings with an option to view all listings.
8.	Sell an item: A form allows users to upload an image, set a price, write a description, and choose a category and condition. Data is stored with a timestamp.
9.	Authentication: Signup and login pages with email and password validation (email addresses must be unique).

How does a user interact with it?
1.	Mouse-driven navigation: Users click category buttons, product images (to view details), the heart icon (to like items), and header buttons (Sell, profile, logout).
2.	Form inputs: Search, filter, sell, sign up, and log in all use standard HTML forms that submit data to the server.
3.	Redirects and feedback: After liking an item, a flash message confirms success. Invalid login or signup attempts show error text. Clicking the "D&B UTSC Market" welcome text returns the user to the homepage.

Special or notable features
1.	Three intelligent homepage sections: New arrivals sorted by timestamp, featured items sorted by like count, and exam essentials filtered by price range and category—directly addressing student needs.
2.	Condition-aware filtering: Five granular condition levels help buyers accurately assess product quality before purchasing.
3.	Like a system with a counter: Encourages social proof and highlights popular items to other users.
4.	Profile separation: Users see their own posts but not others' private information; email is intentionally visible to facilitate direct contact between buyers and sellers.
5.	Image upload handling: Secure filename sanitization and automatic creation of the static/uploads folder.
6.	Session persistence: Users stay logged in across all pages until they explicitly click logout.

Technical overview
Frontend responsibilities
1.	The frontend uses Flask Jinja2 templating with a base.html master template that all other pages extend. Key frontend components include:
2.	CSS files: Separated by page role—common.css for global layout, product.css for product grids, item.css for the detail page, sell.css, login.css, signup.css, profile.css, and index.css.
3.	JavaScript (main.js): Handles client-side navigation for the welcome text, Sell button, Login button, and Signup button. Logout is handled server-side.

Backend/server-side logic
The backend is built with Flask (Python). Below is a summary of key routes and their responsibilities:
Route	Method	Description
/	GET	Index page – fetches new, featured, and exam items 
from database
/category	GET	Shows all items belonging to a selected category
/filter	GET	Processes advanced filters including keyword, price range, 
condition, and sorting
/search	GET	Performs simple keyword search across item names
/item	GET	Displays detailed information for a single item
/like	GET	Adds a like for the current user on an item 
(checks for duplicates)
/like_check	GET	Shows the user's 5 most recently liked items
/like_all	GET	Shows all items the user has liked
/profile	GET	Shows user information and a preview of their 
own listings (5 items)
/profile_post_all	GET	Shows all items the user has posted for sale
/sell	GET/POST	Displays form to list a new item and handles image 
upload and database insertion
/signup	GET/POST	Handles user registration with unique email validation
/login	GET/POST	Authenticates users and establishes a session
/logout	GET	Clears the session and redirects to the homepage

Database usage
The application uses SQLite3 with three tables:
1.	users – Stores user account information
Users (uid, username, email, password)
2.	items – Stores product listings
items (id, name, category, price, image, product_specification, condition, update_timestamp, likes, uid)
3.	likes – Tracks which users liked which items
likes (uid, iid)
4.	Integrity Constraints
items[uid]  users[uid]
likes[uid]  users[uid]
likes[iid]  items[id]

Execution Instructions
Prerequisites
•	Python 3.8 or higher
•	pip (Python package manager)

Dependencies
•	Install Flask and Werkzeug using the following command:
-	Bash
-	pip install Flask werkzeug
•	No additional database drivers are required because SQLite3 is built into Python's standard library

Setup instructions
1.	Download all provided files into a single project folder, maintaining the following structure:
project/
├ app.py
├ templates/
├ base.html
├ index.html
├ category.html
├ filter.html
├ search.html
├ item.html
├ like.html
├ like-all.html
├ profile.html
├ profile-post-all.html
├ sell.html
├ login.html
├ signup.html
├ static/
├ common.css
├ product.css
├ index.css
├ item.css
├ sell.css
├ login.css
├ signup.css
├ profile.css
├ main.js
├ pictures/
├ banner.jpg
├ like.png
├ account.png
├ search_icon.png
2.	Run the application from the terminal:
-	Bash
-	python app.py
3.	Open your browser and navigate to: http://127.0.0.1:5000/
Note: 
•	items.db will be created automatically in the project folder on the first run. 
•	static/uploads/ folder will also be created automatically when you (user) upload the first product image.

Future Improvements
•	Unlike functionality without reloading the webpage: Once an item is liked, click the same button to remove the like, without loading the new page.
•	Edit or delete for listings: Users cannot currently modify or remove their posted items after creation.
•	Pagination: Large result sets, such as "View All" for likes or posts, may become unwieldy and slow to render.
•	Image upload limitations: No file type validation beyond the client-side accept="image/*" attribute, no maximum file size enforcement, and no image preview before upload.
•	Search is name-only: The search feature only searches item names, not within product specifications or category names.
•	Responsive layout Issue: When the browser window is resized (made smaller or pulled to change dimensions), the inherited layout sections (the main content area that extends from base.html) overflow outside their containing boundaries.

Division of work
Team Member	Responsibilities
Jiayi Zhang	•	Import and clean external csv
•	Database Setup, assign randomized data
•	JavaScript navigation handlers (main.js)
•	All buy functions & HTML templates
•	All filter functions & Search bar
•	Sign up & Log in functions & HTML templates
•	Profile functions and HTML templates
•	Index functions & HTML templates
•	Report Writing
	
Ziruo Wang	•	Template Inheritance
•	CSS styling (except for “buy” button)
•	JavaScript navigation handlers (main.js)
•	All Like functions & HTML templates
•	Post/Sell function & HTML templates
•	Category function & HTML templates
•	Profile functions and HTML templates
•	Index functions & HTML templates
•	Report Writing
External Libraries, Frameworks, or Tools
Library/Tool	Purpose	Location of use
Flask	Web framework for routing, request handling, sessions, and templating	app.py – all server-side logic
Werkzeug	Utility library providing secure_filename() for safe file uploads	app.py – in the /sell route
SQLite3	Embedded database for data persistence of users, items, and likes	app.py – all database operations
Jinja2	Templating engine (built into Flask)	All .html files –
template inheritance, loops, and conditionals
Python standard libraries	os, datetime, json	app.py – 
file system operations and timestamp generation
GitHub		
Note: No external CSS tools are used. All styling is custom-written.

References
•	Banner image (banner.jpg) and icons (like.png, account.png, search_icon.png): 
Original assets created specifically for this project.
•	OpenAI ChatGPT: 
Used to assist in writing the image upload handling code in app.py, specifically the file validation, secure filename sanitization using Werkzeug, and the logic for saving uploaded images to the static/uploads/ directory. The implementation follows best practices as outlined in the Werkzeug documentation.
Notes: All code not explicitly covered by the external references listed above is original work created for this project.
