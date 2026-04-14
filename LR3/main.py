import random
import statistics


# Эмуляция замеров RTT для трёх протоколов
def run_pilot_experiment():
    # Симулируем 10 измерений для каждого протокола (в мс)
    ospf_rtt = [45, 52, 48, 47, 55, 49, 51, 46, 50, 53]
    rip_rtt = [78, 82, 75, 80, 79, 81, 77, 83, 76, 80]
    our_rtt = [38, 35, 42, 36, 39, 37, 41, 34, 40, 38]

    print("Результаты пилотного эксперимента")
    print(f"OSPF RTT: среднее = {statistics.mean(ospf_rtt):.1f} мс, std = {statistics.stdev(ospf_rtt):.1f}")
    print(f"RIP RTT:  среднее = {statistics.mean(rip_rtt):.1f} мс, std = {statistics.stdev(rip_rtt):.1f}")
    print(f"Our RTT:  среднее = {statistics.mean(our_rtt):.1f} мс, std = {statistics.stdev(our_rtt):.1f}")

    gain_vs_ospf = (1 - statistics.mean(our_rtt) / statistics.mean(ospf_rtt)) * 100
    print(f"\nВыигрыш нашего алгоритма vs OSPF: {gain_vs_ospf:.1f}%")

    # Проверка гипотезы
    if gain_vs_ospf >= 20:
        print("H1 подтверждается: снижение задержки > 20%")
    else:
        print("H1 не подтверждена")


if __name__ == "__main__":
    run_pilot_experiment()