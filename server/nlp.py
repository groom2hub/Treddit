from functools import cache


@cache
def okt():
    """konlpy Okt 형태소 분석기를 한 번만 만들어 공유한다.

    Okt는 내부적으로 JVM을 띄우는데, JVM을 메인 스레드가 아닌 스레드(FastAPI의 스레드풀 등)에서
    처음 시작하면 프로세스 종료 시 JVM이 정리되지 않아 서버가 멈춘다.
    main.py에서 import 시점(메인 스레드)에 미리 호출해 둔다.
    """
    from konlpy.tag import Okt
    return Okt()
