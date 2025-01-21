from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from database import SessionLocal, Product
from sqlalchemy.future import select
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from typing import Optional
from pydantic import BaseModel
import asyncio

app = FastAPI()

scheduler = AsyncIOScheduler()

class ProductIn(BaseModel):
    artikul: str

class ProductOut(BaseModel):
    name: str
    artikul: str
    price: float
    rating: float
    quantity: int

@app.get("/")
async def root():
    """
    проверка, что сервер fastapi работает
    """
    return {"message": "FastAPI is work"}

async def init_db():
    async_engine = create_async_engine(DATABASE_URL, echo=True)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def fetch_product_data(artikul: str) -> dict:
    """Функция для получения данных товара по артикулу"""
    url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={artikul}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()['data']['products'][0]
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch data from Wildberries")


async def save_product(session: AsyncSession, artikul: str):
    """Функция для сохранения товара в базу данных"""
    product_data = await fetch_product_data(artikul)
    product = Product(
        artikul=artikul,
        name=product_data['name'],
        price=product_data['salePriceU'] / 100,
        rating=product_data['reviewRating'],
        quantity=product_data['totalQuantity']
    )
    session.add(product)
    await session.commit()


@app.post("/api/v1/products", response_model=ProductOut)
async def create_product(
    product: ProductIn, 
    session: AsyncSession = Depends(SessionLocal)
):
    """
    Создает запись о товаре в базе данных
    - **artikul**: Артикул товара, который нужно добавить
    """
    await save_product(session, product.artikul)
    return {"name": product.artikul, "price": 100, "rating": 4.5, "quantity": 20}


async def periodic_update(session: AsyncSession, artikul: str):
    """Функция для периодического обновления данных товара"""
    await save_product(session, artikul)

@app.get("/api/v1/subscribe/{artikul}")
async def subscribe_product(
    artikul: str,
    session: AsyncSession = Depends(SessionLocal)
):
    """
    Подписывается на периодическое обновление данных о товаре по артикулу.
    - **artikul**: Артикул товара.
    """
    job = scheduler.get_job(artikul)
    if not job:
        scheduler.add_job(
            periodic_update,
            IntervalTrigger(minutes=30),
            args=[session, artikul],
            id=artikul,
            replace_existing=True
        )
        return {"message": f"Started periodic updates for {artikul}"}
    else:
        return {"message": f"Periodic updates already running for {artikul}"}


if __name__ == "__main__":
    # Инициализируем базу данных
    asyncio.run(init_db())

    # Запуск планировщика
    scheduler.start()