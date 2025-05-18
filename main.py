import csv
import datetime
import os
from abc import ABC, abstractmethod


def load_hallgatok(fname: str = "adatok.txt") -> list[dict[str, str]]:
    
    here = os.path.dirname(__file__)
    path = os.path.join(here, fname)
    hallgatok = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="	")
        for row in reader:
            
            row["Neptun"] = row["Neptun"].strip().upper()
            row["Név"] = row["Név"].strip()
            hallgatok.append(row)
    return hallgatok


def is_valid_neptun(kod: str, hallgatok: list[dict[str, str]]) -> bool:
    return any(h["Neptun"].upper() == kod.upper() for h in hallgatok)


def get_name_by_neptun(neptun: str, hallgatok: list[dict[str, str]]) -> str:
    for h in hallgatok:
        if h["Neptun"].upper() == neptun.upper():
            return h["Név"]
    return neptun

class Auto(ABC):
    def __init__(self, rendszam: str, tipus: str, ar: float):
        self.rendszam = rendszam
        self.tipus = tipus
        self.ar = ar

    @abstractmethod
    def leiras(self) -> str:
        pass

class Szemelyauto(Auto):
    def __init__(self, rendszam: str, ar: float, ulesek: int):
        super().__init__(rendszam, "Személyautó", ar)
        self.ulesek = ulesek

    def leiras(self) -> str:
        return f"{self.tipus} {self.rendszam} - {self.ulesek} ülés - {self.ar} Ft/nap"

class Teherauto(Auto):
    def __init__(self, rendszam: str, ar: float, kapacitas: int):
        super().__init__(rendszam, "Teherautó", ar)
        self.kapacitas = kapacitas

    def leiras(self) -> str:
        return f"{self.tipus} {self.rendszam} - max {self.kapacitas} kg - {self.ar} Ft/nap"

class Berles:
    def __init__(self, auto: Auto, datum: datetime.date, neptun: str):
        self.auto = auto
        self.datum = datum
        self.neptun = neptun

    def leiras(self, hallgatok: list[dict[str, str]]) -> str:
        nev = get_name_by_neptun(self.neptun, hallgatok)
        return f"{self.datum.isoformat()}: {self.auto.rendszam} – bérelte: {nev} ({self.neptun})"

class Autokolcsonzo:
    def __init__(self):
        self.autok: list[Auto] = []
        self.berlesek: list[Berles] = []

    def add_auto(self, auto: Auto) -> None:
        self.autok.append(auto)

    def berel_auto(self, rendszam: str, datum: datetime.date, neptun: str) -> float:
        if datum < datetime.date.today():
            raise ValueError("Nem lehet múltbeli dátum.")
        for b in self.berlesek:
            if b.auto.rendszam == rendszam and b.datum == datum:
                raise ValueError("Az autó már foglalt erre a napra.")
        auto = next((a for a in self.autok if a.rendszam == rendszam), None)
        if not auto:
            raise ValueError("Nincs ilyen rendszámú autó.")
        b = Berles(auto, datum, neptun)
        self.berlesek.append(b)
        return auto.ar

    def lemond(self, rendszam: str, datum: datetime.date, neptun: str) -> None:
        for b in self.berlesek:
            if b.auto.rendszam == rendszam and b.datum == datum and b.neptun.upper() == neptun.upper():
                self.berlesek.remove(b)
                return
        raise ValueError("Nincs ilyen bérlés.")

    def listaz(self, hallgatok: list[dict[str, str]]) -> list[str]:
        return [b.leiras(hallgatok) for b in self.berlesek]


def init_minta() -> Autokolcsonzo:
    k = Autokolcsonzo()
    k.add_auto(Szemelyauto("ZZZ-111", 9500, 5))
    k.add_auto(Teherauto("QWE-234", 18000, 1200))
    k.add_auto(Szemelyauto("RTY-345", 11000, 4))
    today = datetime.date.today()
    k.berlesek.append(Berles(k.autok[0], today + datetime.timedelta(days=1), "ABC123"))
    k.berlesek.append(Berles(k.autok[1], today + datetime.timedelta(days=2), "XYZ456"))
    k.berlesek.append(Berles(k.autok[2], today + datetime.timedelta(days=3), "HTT404"))
    k.berlesek.append(Berles(k.autok[0], today + datetime.timedelta(days=4), "ASD789"))
    return k

def main() -> None:
    hallgatok = load_hallgatok()
    kolcsonzo = init_minta()
    print("=== Autókölcsönző ===")
    while True:
        print("\n1) Autó bérlése")
        print("2) Bérlés lemondása")
        print("3) Bérlések listázása")
        print("4) Kilépés")
        cmd = input("Válassz: ").strip()
        try:
            if cmd == "1":
                rendszam = input("Rendszám: ").strip().upper()
                datum_str = input("Dátum (YYYY-MM-DD): ").strip()
                neptun = input("Neptun kód: ").strip().upper()
                if not is_valid_neptun(neptun, hallgatok):
                    print("Ismeretlen Neptun-kód.")
                    continue
                datum = datetime.datetime.strptime(datum_str, "%Y-%m-%d").date()
                ar = kolcsonzo.berel_auto(rendszam, datum, neptun)
                print(f"Sikeres bérlés, fizetendő {ar} Ft")
            elif cmd == "2":
                rendszam = input("Rendszám: ").strip().upper()
                datum_str = input("Dátum (YYYY-MM-DD): ").strip()
                neptun = input("Neptun kód: ").strip().upper()
                datum = datetime.datetime.strptime(datum_str, "%Y-%m-%d").date()
                kolcsonzo.lemond(rendszam, datum, neptun)
                print("Bérlés lemondva.")
            elif cmd == "3":
                print("\nAktuális bérlések:")
                for sor in kolcsonzo.listaz(hallgatok):
                    print(" -", sor)
            elif cmd == "4":
                print("Viszlát!")
                break
            else:
                print("Érvénytelen választás.")
        except Exception as e:
            print("Hiba:", e)

if __name__ == "__main__":
    main()
