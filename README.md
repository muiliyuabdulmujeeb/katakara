# Katakara – Modular E-commerce Backend API

Katakara is a **scalable, role-aware e-commerce backend API** built with **Django Rest Framework**. It supports **multi-role users**, **JWT authentication**, **product moderation**, **cart-to-order workflows**, and a **manual payment confirmation pipeline** designed to evolve into full payment gateway integration.

This project was **designed feature-by-feature from scratch**, with a strong emphasis on:

- Clear domain boundaries
- Explicit state transitions
- Role-based access control
- Future extensibility

---

## Core Principles

- **Explicit workflows** (no magic transitions)
- **JWT-based stateless authentication**
- **Separation of concerns** (auth, product, cart, order)
- **Admin-verified actions** (payments, approvals)
- **UUID-first architecture**

---

## Tech Stack

- Python
- Django
- Django Rest Framework
- SimpleJWT (JWT Authentication)
- PostgreSQL
- UUIDs for all primary keys

---

## Authentication System

Katakara uses **JWT authentication** with **SimpleJWT**.

### Token Design

- **Access Token**: 5 minutes
- **Refresh Token**: 7 days (rotated)
- Tokens include:
  - `user_id` (UUID)
  - roles
  - expiration metadata

### Auth Features

- Signup (auto-login)
- Login
- Logout (refresh token blacklist)
- Token refresh
- Forgot password / reset password
- Role upgrade request & approval system

---

## User Roles & Access Model

### Roles

- **Buyer**
- **Seller**
- **Admin**
- **Superadmin**

### Role Rules

- Users may have **multiple roles** (buyer + seller)
- Admin/Superadmin roles are **exclusive**
- Users **cannot self-assign admin roles**
- Role upgrades require **admin approval**

Roles are implemented using:

- Django Groups
- Custom permissions
- Explicit request–approval workflow

---

## Product System

### Product Lifecycle

Products follow a **strict moderation lifecycle**:

```
pending → approved → rejected → blacklisted → deleted
```

### Product Features

- Create product (seller)
- Edit product (owner only)
- Delete product (soft delete via status)
- View product details
- List approved products (public)
- List unapproved products (admin only)
- Approve product (admin/superadmin)
- Reject product (admin/superadmin)
- Blacklist product (admin/superadmin)

### Categories

- UUID-based
- Slug-driven
- Activatable (`is_active`)

---

## Cart System

The cart system acts as a **temporary workspace**, not a financial record.

### Cart Design

- One cart per user (`OneToOne`)
- Session-based cart for guests
- Cart items store:
  - product snapshot
  - quantity
  - price at time of add

### Cart Features

- Create cart automatically
- View cart
- Add item to cart
- Update item quantity
- Remove item
- Clear cart

Cart is **not immutable** and does not represent a commitment to buy.

---

## Order (Purchase) System

Orders are **immutable snapshots** created from carts.

### Order Status Lifecycle

```
draft
  ↓
saved
  ↓
awaiting_payment
  ↓ (buyer confirms payment)
payment_pending
  ↓ (seller/admin confirms)
paid
```

### Order Features

- Create order from cart
- Save order for later
- Delete/cancel order
- View own orders
- View order details
- Manual payment workflow
- Seller/admin payment confirmation

Orders support:

- Authenticated users
- Guest checkout (via session key)

---

## Manual Payment Workflow

Katakara currently uses a **manual payment confirmation system**, designed to be replaced by a payment gateway later.

### Payment Steps

1. Buyer initiates payment (`awaiting_payment`)
2. Buyer confirms payment (`payment_pending`)
3. Seller/Admin confirms or rejects payment
4. Order becomes `paid`

This design:

- Prevents fake confirmations
- Supports offline/manual payments
- Allows audit trails

---

## Review System (Planned)

- One review per user per product
- Review allowed only after purchase
- Admin moderation supported
- Rating + comment system

---

## App Documentation
Katakara provides interactive API documentation via Swagger UI and Redoc.

- Swagger UI: `/schema/docs/`
- OpenAPI schema: `/schema/`
- Redoc schema: `/schema/redoc`

This documentation allows developers to:
- Inspect request/response formats
- Test endpoints directly
- View authentication requirements


---

## Setup Instructions

```bash
git clone https://github.com/muiliyuabdulmujeeb/katakara.git
cd katakara
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Environment Variables

```env
check .env.example file
```

---

## Testing Strategy (Recommended)

- Unit tests for serializers
- Integration tests for workflows
- Permission-based tests for roles
- State transition tests for orders

---

## Roadmap

- Payment gateway integration
- Order delivery system
- Dispute management
- Notifications (email/websocket)
- Analytics & reporting
- Inventory locking
- Refund workflows

---

## Contribution Guidelines

- Follow explicit state transitions
- No implicit permission escalation
- Use UUIDs consistently
- Keep serializers thin and intentional

---

---

## Final Note

Katakara was designed **deliberately**, not rushed. Every feature follows **real-world e-commerce logic**, making the project easy to extend, debug, and scale.