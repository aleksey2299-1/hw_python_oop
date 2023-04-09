from dataclasses import dataclass, asdict
from typing import Type


@dataclass
class InfoMessage:
    """Информационное сообщение о тренировке."""
    training_type: str
    duration: float
    distance: float
    speed: float
    calories: float
    message: str = (
        'Тип тренировки: {training_type}; '
        'Длительность: {duration:.3f} ч.; '
        'Дистанция: {distance:.3f} км; '
        'Ср. скорость: {speed:.3f} км/ч; '
        'Потрачено ккал: {calories:.3f}.'
    )

    def get_message(self) -> str:
        return self.message.format(**asdict(self))


@dataclass
class Training:
    """Базовый класс тренировки."""
    H_IN_M: float = 60.0
    M_IN_KM: float = 1000.0
    LEN_STEP: float = 0.65

    def __init__(
        self,
        action: int,
        duration: float,
        weight: float,
    ) -> None:
        self.action = action
        self.duration_h = duration
        self.weight_kg = weight

    def get_distance(self) -> float:
        """Получить дистанцию в км."""
        return self.action * self.LEN_STEP / self.M_IN_KM

    def get_mean_speed(self) -> float:
        """Получить среднюю скорость движения в км/ч."""
        return self.get_distance() / self.duration_h

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        raise NotImplementedError(
            f'{self.__class__.__name__} '
            'не имеет функции подсчета калорий.'
        )

    def show_training_info(self) -> InfoMessage:
        """Вернуть информационное сообщение о выполненной тренировке."""
        return InfoMessage(
            self.__class__.__name__,
            self.duration_h,
            self.get_distance(),
            self.get_mean_speed(),
            self.get_spent_calories(),
        )


class Running(Training):
    """Тренировка: бег."""
    CALORIES_MEAN_SPEED_MULTIPLIER: float = 18.0
    CALORIES_MEAN_SPEED_SHIFT: float = 1.79

    def get_spent_calories(self) -> float:
        """Получить кол-во затраченных калорий для бега."""
        minutes: float = self.duration_h * self.H_IN_M
        return (
            (self.CALORIES_MEAN_SPEED_MULTIPLIER * self.get_mean_speed()
             + self.CALORIES_MEAN_SPEED_SHIFT)
            * self.weight_kg / self.M_IN_KM * minutes
        )


class SportsWalking(Training):
    """Тренировка: спортивная ходьба."""
    COEF_WEIGHT: float = 0.035
    MEAN_SPEED_IN_2_AND_HEIGHT: float = 0.029
    KM_PER_H_IN_M_IN_S: float = 0.278
    SM_IN_M: float = 100.0

    def __init__(
        self,
        action: int,
        duration: float,
        weight: float,
        height: float,
    ) -> None:
        super().__init__(action, duration, weight)
        self.height_sm = height

    def get_spent_calories(self) -> float:
        """Подсчет калорий при спортивной хотьбе.
        Предварительно подсчитываем минуты и высоту в метрах.
        """
        minutes: float = self.duration_h * self.H_IN_M
        height_in_metres: float = self.height_sm / self.SM_IN_M
        return (
            (self.COEF_WEIGHT * self.weight_kg
             + ((self.get_mean_speed() * self.KM_PER_H_IN_M_IN_S) ** 2
                / height_in_metres) * self.MEAN_SPEED_IN_2_AND_HEIGHT
             * self.weight_kg) * minutes
        )


class Swimming(Training):
    """Тренировка: плавание."""
    LEN_STEP: float = 1.38
    MEAN_SPEED_MOVE: float = 1.1
    SPEED_MULTIPLIER: float = 2.0

    def __init__(
        self,
        action: int,
        duration: float,
        weight: float,
        length_pool: float,
        count_pool: float,
    ) -> None:
        super().__init__(action, duration, weight)
        self.length_pool_m = length_pool
        self.count_pool = count_pool

    def get_mean_speed(self) -> float:
        """Переопределяем функцию расчёта средней скорости для плавания."""
        return (
            self.length_pool_m * self.count_pool
            / self.M_IN_KM / self.duration_h
        )

    def get_spent_calories(self) -> float:
        """Получить кол-во затраченных калорий для плавания."""
        return (
            (self.get_mean_speed() + self.MEAN_SPEED_MOVE)
            * self.SPEED_MULTIPLIER * self.weight_kg * self.duration_h
        )


def read_package(workout_type: str, data: list[float]) -> Training:
    """Расшифровываем пакет данных."""
    trainings: dict[str, Type[Training]] = {
        'SWM': Swimming,
        'RUN': Running,
        'WLK': SportsWalking,
    }
    try:
        trainings[workout_type](*data)
    except KeyError:
        print('Ошибка KeyError: не верно задан тип тренировки')
    except TypeError:
        print('Ошибка TypeError: ошибка переданных данных')
    else:
        return trainings[workout_type](*data)


def main(training: Training) -> None:
    """Главная функция."""
    info: InfoMessage = training.show_training_info()
    print(info.get_message())


if __name__ == '__main__':
    packages = [
        ('SWM', [720, 1, 80, 25, 40]),
        ('RUN', [15000, 1, 75]),
        ('WLK', [9000, 1, 75, 180]),
    ]

    for workout_type, data in packages:
        training = read_package(workout_type, data)
        if training:
            main(training)
