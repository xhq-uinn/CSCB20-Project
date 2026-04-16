# D&B UTSC Marketplace

**University of Toronto Scarborough (UTSC)**  
**Team: D&B Master**  
Jiayi Zhang, Ziruo Wang  
April 17, 2026  

---

##  Overview

D&B UTSC Marketplace is a peer-to-peer e-commerce platform designed specifically for the UTSC community.

Unlike traditional marketplaces, this system does not support online payments. Instead, buyers and sellers connect directly after expressing interest, allowing them to negotiate prices and arrange exchanges in a trusted campus environment.

---

## Features

### Browsing & Discovery
- Browse items by 17 categories  
- Keyword-based search  
- Advanced filtering:
  - Price range  
  - Condition  
  - Popularity / recency  

### User Interaction
- Like items (1 like per user per item)  
- View:
  - Recent liked items (top 5)  
  - All liked items  

### Selling
- Post items with:
  - Image upload  
  - Price  
  - Description  
  - Category & condition  
- Automatic timestamping  

### Profile
- View user information (email visible for contact)  
- Preview and view all posted listings  

### Authentication
- Signup with unique email  
- Login/logout with session persistence  

---

## System Design

### Navigation
All pages share a unified header:
- Search bar  
- Like shortcut  
- Profile access  
- Login / logout  
- Sell button  

---

### Homepage Sections
- **New Arrivals** → sorted by time  
- **Featured Items** → most liked  
- **Exam Essentials** → Stationery ($10–$50)  

---

### Categories
Includes:
- Automotive  
- Clothing  
- Footwear  
- Furniture  
- Electronics  
- Stationery  
- (17 categories total)

---

### Filtering
Users can filter by:
- Keyword  
- Price range  
- Condition:
  - Brand New  
  - Like New  
  - Minor Scratches  
  - Visible Scratches  
  - Poor Condition  
- Sorting:
  - Price (low → high / high → low)  
  - Most liked  
  - Most recent  

---

### Item Page
Displays:
- Image  
- Name  
- Price  
- Category  
- Condition  
- Description  
- Like count  

---

## User Interaction Flow

1. Mouse-driven navigation  
   - Click categories, items, and buttons  

2. Form-based input  
   - Search, filter, login, signup, sell  

3. Feedback system  
   - Flash messages (e.g., like success)  
   - Error messages (invalid login)  

---

## Notable Features

- Smart homepage sections tailored for students  
- Like system for social proof  
- Detailed condition classification  
- Session persistence  
- Secure image upload (sanitized filenames)  
- Direct buyer-seller communication via email  

---

## Tech Stack

### Frontend
- HTML (Jinja2 templates)  
- CSS (modular stylesheets)  
- JavaScript (main.js)  

### Backend
- Python + Flask  

### Database
- SQLite3  

---

## Backend Routes

| Route | Method | Description |
|------|--------|------------|
| `/` | GET | Homepage (new, featured, exam items) |
| `/category` | GET | Items by category |
| `/filter` | GET | Advanced filtering |
| `/search` | GET | Keyword search |
| `/item` | GET | Item details |
| `/like` | GET | Like an item |
| `/like_check` | GET | Recent liked items |
| `/like_all` | GET | All liked items |
| `/profile` | GET | User profile |
| `/profile_post_all` | GET | All user posts |
| `/sell` | GET/POST | Create item |
| `/signup` | GET/POST | Register |
| `/login` | GET/POST | Login |
| `/logout` | GET | Logout |

---

## Database Schema

The application uses **SQLite3** with three main tables: `users`, `items`, and `likes`.

---

### Users Table

- users(uid, username, email, password)
- items(id, name, category, price, image, product_specification, condition, update_timestamp, likes, uid)
- likes(uid, iid)

### Integrity Constraints
- items.uid ⊆ users.uid
- likes.uid ⊆ users.uid
- likes.iid ⊆ items.id

Note: 	
- uid is the unique identifier for users
- id (in items) is the unique identifier for products
- The likes table uses a composite primary key (uid, iid) to prevent duplicate likes
- The likes count in the items table is stored for faster query performance (denormalization)
