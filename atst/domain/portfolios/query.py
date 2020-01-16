from sqlalchemy import or_
from atst.database import db
from atst.domain.common import Query
from atst.models.portfolio import Portfolio
from atst.models.portfolio_role import PortfolioRole, Status as PortfolioRoleStatus
from atst.models.application_role import (
    ApplicationRole,
    Status as ApplicationRoleStatus,
)
from atst.models.application import Application


class PortfoliosQuery(Query):
    model = Portfolio

    @classmethod
    def get_for_user(cls, user):
        return (
            db.session.query(Portfolio)
            .filter(
                or_(
                    Portfolio.id.in_(
                        db.session.query(Portfolio.id)
                        .join(Application)
                        .filter(Portfolio.id == Application.portfolio_id)
                        .filter(
                            Application.id.in_(
                                db.session.query(Application.id)
                                .join(ApplicationRole)
                                .filter(
                                    ApplicationRole.application_id == Application.id
                                )
                                .filter(ApplicationRole.user_id == user.id)
                                .filter(
                                    ApplicationRole.status
                                    == ApplicationRoleStatus.ACTIVE
                                )
                                .filter(ApplicationRole.deleted == False)
                                .subquery()
                            )
                        )
                    ),
                    Portfolio.id.in_(
                        db.session.query(Portfolio.id)
                        .join(PortfolioRole)
                        .filter(PortfolioRole.user == user)
                        .filter(PortfolioRole.status == PortfolioRoleStatus.ACTIVE)
                        .subquery()
                    ),
                )
            )
            .filter(Portfolio.deleted == False)
            .order_by(Portfolio.name.asc())
            .all()
        )

    @classmethod
    def create_portfolio_role(cls, user, portfolio, **kwargs):
        return PortfolioRole(user=user, portfolio=portfolio, **kwargs)
