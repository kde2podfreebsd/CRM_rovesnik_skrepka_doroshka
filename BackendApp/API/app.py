from fastapi import FastAPI
from BackendApp.API.files.router import router as files_router
from BackendApp.API.event.router import router as event_router
from BackendApp.API.ticket.router import router as ticket_router
from BackendApp.API.lineup.router import router as lineup_router
from BackendApp.API.test.router import router as test_router
from BackendApp.API.quiz.router import router as quiz_router
from BackendApp.API.referrals.router import router as referrals_router
from BackendApp.API.affilate_promotions.router import router as affilate_promotion_router
from BackendApp.API.acquiring.router import router as acquiring_router
from BackendApp.API.promocodes.router import router as promocodes_router
from BackendApp.API.client.router import router as client_router
from BackendApp.API.reservation.router import router as reservation_router
from BackendApp.API.table.router import router as table_router
from BackendApp.API.partner_gift.router import router as partner_gift_router
from BackendApp.API.review.router import router as review_router
from BackendApp.API.transaction.router import router as transaction_router
from BackendApp.API.mailing.router import router as mailing_router
from BackendApp.API.client_action_log.router import router as log_router
from BackendApp.API.faq.router import router as faq_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(files_router, prefix="/api")
app.include_router(event_router, prefix="/api")
app.include_router(ticket_router, prefix="/api")
app.include_router(lineup_router, prefix="/api")
app.include_router(test_router, prefix="/api")
app.include_router(quiz_router, prefix="/api")
app.include_router(affilate_promotion_router, prefix="/api")
app.include_router(acquiring_router, prefix="/api")
app.include_router(referrals_router, prefix="/api")
app.include_router(promocodes_router, prefix="/api")
app.include_router(client_router, prefix="/api")
app.include_router(reservation_router, prefix="/api")
app.include_router(table_router, prefix="/api")
app.include_router(partner_gift_router, prefix="/api")
app.include_router(review_router, prefix="/api")
app.include_router(transaction_router, prefix="/api")
app.include_router(mailing_router, prefix="/api")
app.include_router(log_router, prefix="/api")
app.include_router(faq_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
