from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.core.exceptions import CustomerAlreadyExistsError, CustomerNotFoundError
from app.dependencies import get_customer_service
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/api/v1/customers", tags=["Customers"])


@router.get(
    "/search",
    response_model=List[CustomerResponse],
    status_code=status.HTTP_200_OK,
    summary="Search customers by partial name or email",
    description="Performs a case-insensitive substring search across customer names and email addresses.",
)
def search_customers(
    q: str = Query(
        ...,
        min_length=2,
        max_length=100,
        description="Search term (minimum 2 non-whitespace characters, maximum 100 characters)",
    ),
    service: CustomerService = Depends(get_customer_service),
) -> List[CustomerResponse]:
    trimmed_query = q.strip()
    if len(trimmed_query) < 2:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["query", "q"],
                    "msg": "Search query must contain at least 2 non-whitespace characters.",
                    "type": "value_error.min_length",
                }
            ],
        )
    return service.search_customers(trimmed_query)


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new customer",
    description="Registers a new customer record with a unique identifier and timestamp.",
)
def create_customer(
    customer_in: CustomerCreate,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    try:
        return service.create_customer(customer_in)
    except CustomerAlreadyExistsError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(err),
        ) from err


@router.get(
    "",
    response_model=List[CustomerResponse],
    status_code=status.HTTP_200_OK,
    summary="List all customers",
    description="Retrieves the complete collection of registered customers.",
)
def get_all_customers(
    service: CustomerService = Depends(get_customer_service),
) -> List[CustomerResponse]:
    return service.get_all_customers()


@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
    summary="Partially update a customer",
    description="Updates a customer's name and/or email. `id` and `created_at` are immutable.",
)
def update_customer(
    customer_id: str,
    customer_in: CustomerUpdate,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    try:
        return service.update_customer(customer_id, customer_in)
    except CustomerNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except CustomerAlreadyExistsError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(err),
        ) from err


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a customer",
    description="Permanently removes a customer record from the JSON store.",
)
def delete_customer(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service),
) -> Response:
    try:
        service.delete_customer(customer_id)
    except CustomerNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    return Response(status_code=status.HTTP_204_NO_CONTENT)
