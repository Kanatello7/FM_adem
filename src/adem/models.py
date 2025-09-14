#from src.db import Base
#from sqlalchemy import String, Boolean, Integer, CheckConstraint
#from sqlalchemy.orm import Mapped, mapped_column
#
#class CounterParty(Base):
#    id: Mapped[int] = mapped_column(Integer, primary_key=True)
#    name: Mapped[str] = mapped_column(String(1024))
#    iic: Mapped[str] = mapped_column(String(256), nullable=True) 
#    bin_or_iin: Mapped[str] = mapped_column(String(256), nullable=True)
#    in_blacklist: Mapped[bool] = mapped_column(Boolean, default=False)
#    days_to_add: Mapped[int] = mapped_column(Integer, nullable=True)
#    
#    __table_args__ = (
#        CheckConstraint('days_to_add' > 0, name="check_days_to_add_positive"),
#    )    
#
#    def __str__(self):
#        return self.name
