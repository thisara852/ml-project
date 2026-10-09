from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Review, Favorite, Destination, User
from app.schemas.schemas import ReviewCreate, ReviewResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews & Ratings"])


@router.post("/", response_model=ReviewResponse)
def submit_review(
    review_in: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    destination = db.query(Destination).filter(Destination.id == review_in.destination_id).first()
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")

    review = Review(
        user_id=current_user.id,
        destination_id=review_in.destination_id,
        rating=review_in.rating,
        comment=review_in.comment
    )
    db.add(review)

    # Update destination average rating and review count
    all_reviews = db.query(Review.rating).filter(Review.destination_id == destination.id).all()
    ratings_sum = sum(r[0] for r in all_reviews) + review_in.rating
    new_count = len(all_reviews) + 1
    destination.rating = round(ratings_sum / new_count, 1)
    destination.num_reviews = new_count

    db.commit()
    db.refresh(review)

    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        destination_id=review.destination_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
        user_name=current_user.full_name
    )


@router.get("/destination/{destination_id}", response_model=List[ReviewResponse])
def get_destination_reviews(destination_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review, User.full_name).join(User, Review.user_id == User.id).filter(
        Review.destination_id == destination_id
    ).order_by(Review.created_at.desc()).all()

    results = []
    for r, full_name in reviews:
        results.append(ReviewResponse(
            id=r.id,
            user_id=r.user_id,
            destination_id=r.destination_id,
            rating=r.rating,
            comment=r.comment,
            created_at=r.created_at,
            user_name=full_name
        ))
    return results


@router.post("/favorites/{destination_id}")
def toggle_favorite(
    destination_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    fav = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.destination_id == destination_id
    ).first()

    if fav:
        db.delete(fav)
        db.commit()
        return {"favorited": False, "message": "Removed from favorites"}
    else:
        new_fav = Favorite(user_id=current_user.id, destination_id=destination_id)
        db.add(new_fav)
        db.commit()
        return {"favorited": True, "message": "Added to favorites"}


@router.get("/favorites/my")
def get_my_favorites(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    favs = db.query(Destination).join(Favorite, Favorite.destination_id == Destination.id).filter(
        Favorite.user_id == current_user.id
    ).all()
    return favs
