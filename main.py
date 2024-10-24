from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import create_engine, Column, Integer, String, Float, Table, ForeignKey, and_
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session, joinedload
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получаем параметры подключения к базе данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")


# Инициализация базы данных
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Таблица связей для "многие ко многим"
item_category_association = Table(
    'item_category', Base.metadata,
    Column('item_id', Integer, ForeignKey('items.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)


class Item(Base):
    """Определение таблицы "items"""
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, default=None)
    price = Column(Float, nullable=False)
    categories = relationship("Category", secondary=item_category_association, back_populates="items")


class Category(Base):
    """Определение таблицы "categories"""
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    items = relationship("Item", secondary=item_category_association, back_populates="categories")


# Создание таблиц
Base.metadata.create_all(engine)

# Настройка сессии для взаимодействия с БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Инициализация FastAPI
app = FastAPI()


# Зависимость для сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic-схемы для валидации данных
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class ItemCreate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: int
    categories: List[str] = []

    class Config:
        from_attribute = True


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    items: List[ItemResponse] = []

    class Config:
        from_attribute = True


# Маршруты для работы с товарами (items)
@app.post("/items/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Роут для создания товара"""
    db_item = Item(name=item.name, description=item.description, price=item.price)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return ItemResponse(
        id=db_item.id,
        name=db_item.name,
        description=db_item.description,
        price=db_item.price,
        categories=[category.name for category in db_item.categories]  # Возвращаем список названий категорий
    )


@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    """Роут для обновления товара"""
    db_item = db.query(Item).get(item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Товар не найден")

    db_item.name = item.name
    db_item.description = item.description
    db_item.price = item.price
    db.commit()
    db.refresh(db_item)
    return ItemResponse(
        id=db_item.id,
        name=db_item.name,
        description=db_item.description,
        price=db_item.price,
        categories=[category.name for category in db_item.categories]  # Преобразуем категории в список названий
    )


@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Роут для удаления товара"""
    db_item = db.query(Item).get(item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Товар не найден")

    db.delete(db_item)
    db.commit()
    return {"message": "Товар удален"}


# Маршруты для работы с категориями (categories)
@app.post("/categories/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Роут для создания категории"""
    existing_category = db.query(Category).filter_by(name=category.name).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Категория с таким именем уже существует")

    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@app.get("/categories/", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Роут для получения всех категорий"""
    categories = db.query(Category).all()
    return [
        CategoryResponse(
            id=category.id,
            name=category.name,
            items=[ItemResponse(
                id=item.id,
                name=item.name,
                description=item.description,
                price=item.price,
                categories=[cat.name for cat in item.categories]  # Сериализация категорий
            ) for item in category.items]
        )
        for category in categories
    ]


@app.post("/categories/{category_id}/items/{item_id}", response_model=ItemResponse)
def add_item_to_category(category_id: int, item_id: int, db: Session = Depends(get_db)):
    """Роут для добавления товаров в категорию"""
    category = db.query(Category).get(category_id)
    item = db.query(Item).get(item_id)

    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    if not item:
        raise HTTPException(status_code=404, detail="Товар не найден")

    # Проверяем, что товар еще не добавлен в категорию
    if item not in category.items:
        category.items.append(item)
        db.commit()

    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        price=item.price,
        categories=[category.name for category in item.categories]  # Преобразуем категории в список названий
    )


@app.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category: CategoryCreate,
    item_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db)
):
    """Роут для обновления категории и её товаров"""
    db_category = db.query(Category).get(category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    # Проверяем, что новое имя категории не занято
    existing_category = db.query(Category).filter(category.name == Category.name).first()
    if existing_category and existing_category.id != category_id:
        raise HTTPException(status_code=400, detail="Категория с таким именем уже существует")

    # Обновляем имя категории
    db_category.name = category.name

    # Если переданы item_ids, обновляем товары в категории
    if item_ids is not None:
        items = db.query(Item).filter(Item.id.in_(item_ids)).all()

        # Проверяем, что все переданные товары существуют
        if len(items) != len(item_ids):
            raise HTTPException(status_code=404, detail="Один или несколько товаров не найдены")

        db_category.items = items

    # Применяем изменения
    db.commit()
    db.refresh(db_category)

    return CategoryResponse(
        id=db_category.id,
        name=db_category.name,
        items=[
            ItemResponse(
                id=item.id,
                name=item.name,
                description=item.description,
                price=item.price,
                categories=[cat.name for cat in item.categories]  # Преобразуем категории в список названий
            )
            for item in db_category.items
        ]
    )


@app.get("/items", response_model=List[ItemResponse])
def filter_items(
    categories: Optional[List[str]] = Query(None),
    min_price: Optional[float] = Query(0),
    max_price: Optional[float] = Query(float('inf')),
    db: Session = Depends(get_db)
):
    """Роут для фильтрации товаров по категориям и диапазону цен"""
    query = db.query(Item).options(joinedload(Item.categories))  # Подгружаем связанные категории

    # Фильтрация по категориям, если они указаны
    if categories:
        query = query.join(Item.categories).filter(Category.name.in_(categories))

    # Фильтрация по диапазону цен
    query = query.filter(and_(Item.price >= min_price, Item.price <= max_price))

    # Получаем результат
    items = query.all()

    if not items:
        raise HTTPException(status_code=404, detail="Товары не найдены")

    return [
        ItemResponse(
            id=item.id,
            name=item.name,
            description=item.description,
            price=item.price,
            categories=[category.name for category in item.categories]  # Преобразуем категории в список названий
        )
        for item in items
    ]
