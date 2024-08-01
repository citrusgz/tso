import subprocess
import os
import time

def print_ascii_art():
    ascii_art = """                   
  _______ _____           ____          _      _    _  ____  
 |__   __|  __ \    /\   |  _ \   /\   | |    | |  | |/ __ \ 
    | |  | |__) |  /  \  | |_) | /  \  | |    | |__| | |  | |
    | |  |  _  /  / /\ \ |  _ < / /\ \ | |    |  __  | |  | |
    | |  | | \ \ / ____ \| |_) / ____ \| |____| |  | | |__| |
    |_|  |_|  \_\_/    \_\____/_/    \_\______|_|  |_|\____/ 
                                                             
                                                                                                                                                                                                      
                             ..--                            
                      ------------------                    
                      ------------------                    
                      ------------------                    
                ##    ----------..------    ##              
            ######    ------------------    ######          
            ######    ------------------    ######          
            ######    ------------------    ######          
            ######    ----------..------    ######    ++    
            ######    ------------------    ######    ++    
    ++++    ######    ------------------    ######    ++++  
    ++++    ######    ------------------    ######    ++++  
  ++++++    ######    ----------..------    ######    ++++++
  ++++++    ######    ------------------    ######    ++++++
  ++++++    ######    ------------------    ######    ++++++
  ++++++    ######    ------------------    ######    ++++++
++++++++    ######    --..------..------    ######    ++++++
  ++++++    ######    ------------------    ######    ++++++
  ++++++    ######    ------------------    ######    ++++++
  ++++++    ######    ------------------    ######    ++++++
  ++++++    ######                          ######    ++++  
    ++++    ######                          ######    ++++  
    ++++    ######################################    ++    
      ++    ######################################    ++    
            ######################################          
                                                            
                                                            
              ++++++++++++++++++++++++++++++++++            
                  ++++++++++++++++++++++++++                
                      ++++++++++++++++++          
    _____ _____  _____ _______ ______ __  __           _____ 
  / ____|_   _|/ ____|__   __|  ____|  \/  |   /\    / ____|
 | (___   | | | (___    | |  | |__  | \  / |  /  \  | (___  
  \___ \  | |  \___ \   | |  |  __| | |\/| | / /\ \  \___ \ 
  ____) |_| |_ ____) |  | |  | |____| |  | |/ ____ \ ____) |
 |_____/|_____|_____/   |_|  |______|_|  |_/_/    \_\_____/ 
                                                            
   ____  _____  ______ _____           _____ _____ ____  _   _          _____  _____ 
  / __ \|  __ \|  ____|  __ \    /\   / ____|_   _/ __ \| \ | |   /\   |_   _|/ ____|
 | |  | | |__) | |__  | |__) |  /  \ | |      | || |  | |  \| |  /  \    | | | (___  
 | |  | |  ___/|  __| |  _  /  / /\ \| |      | || |  | | . ` | / /\ \   | |  \___ \ 
 | |__| | |    | |____| | \ \ / ____ \ |____ _| |_ |__| | |\  |/ ____ \ _| |_ ____) |
  \____/|_|    |______|_|  \_\_/    \_\_____|_____\____/|_| \_/_/    \_\_____|_____/ 
                                                                                     
                                                                                             
    """
    print(ascii_art)
    
# Calcula o tempo de CPU consumido pelo processo por parte do usuário (em segundos)
def get_user_cpu_time(pid):
    with open(f'/proc/{pid}/stat') as f:
        fields = f.read().split()
        utime = int(fields[13])
        return utime / os.sysconf(os.sysconf_names['SC_CLK_TCK'])


# Calcula o tempo de CPU consumido pelo processo por parte do sistema (em segundos)
def get_system_cpu_time(pid):
    with open(f'/proc/{pid}/stat') as f:
        fields = f.read().split()
        stime = int(fields[14])
        return stime / os.sysconf(os.sysconf_names['SC_CLK_TCK'])

# Executa o processo e monitora o tempo de CPU e o tempo de clock
def execute_process(bin_path, set_cpu_time, set_clock_time):
    try:
        # Lança o processo e obtém o ID
        process = subprocess.Popen([bin_path])
        pid = process.pid
        print(f"PID do processo lançado: {pid}")

        # Começa a mensurar o tempo de relógio
        start_clock_time = time.time()

        # Monitora o processo enquanto ele estiver em execução ou até que seja excedido o tempo de relógio
        while process.poll() is None:
            # Aguarda 1 segundo para verificar o consumo de CPU e o tempo de relógio
            time.sleep(1)
            # Calcula o tempo de relógio atual
            current_clock_time = time.time() - start_clock_time
            # Obtém o tempo de CPU consumido pelo processo por parte do usuário
            user_cpu_time = get_user_cpu_time(pid)
            # Obtém o tempo de CPU consumido pelo processo por parte do sistema
            system_cpu_time = get_system_cpu_time(pid)
            # Calcula o tempo de relógio restante
            remaining_clock_time = set_clock_time - current_clock_time
            # Calcula a cota de CPU restante
            remaining_quota = set_cpu_time - (user_cpu_time + system_cpu_time)

            print(f"Tempo restante de relógio: {max(0, remaining_clock_time)} segundos")
            print(f"Consumo da cota de CPU (user): {user_cpu_time} segundos")
            print(f"Consumo da cota de CPU (system): {system_cpu_time} segundos")
            print(f"Consumo total de CPU: {remaining_quota} segundos")

            # Verifica se foi excedido o tempo, se sim, encerra o processo
            if current_clock_time > set_clock_time:
                print("O processo excedeu o limite de tempo e será encerrado.")
                process.kill()
                break

            # Verifica se a cota de CPU foi excedida e exibe o alerta
            if remaining_quota < 0:
                print(f"O processo excedeu o limite de cota. Seu consumo total é {user_cpu_time + system_cpu_time} segundos. Pague o valor correspondente.")
                process.kill()
                break

        # Calcula o tempo de relógio restante e retorna o valor para o loop principal
        return max(0, remaining_clock_time)

    except KeyboardInterrupt:
        print("Operação interrompida pelo usuário.")


def main():
    # Exibe o banner e pede o nome do binário a ser executado já com o caminho
    print_ascii_art()
    bin_name = input("Digite o nome do binário a ser executado: ").strip()
    bin_path = os.path.join("/usr/bin", bin_name)

    # Pede a cota de CPU e o tempo de relógio
    set_cpu_time = int(input("Digite a cota de CPU que será usada (em segundos): ").strip())
    set_clock_time = int(input("Digite a cota de tempo que será usada em segundos: ").strip())

    # Verifica se o binário é um arquivo e se é executável, se a verificação falhar, exibe uma mensagem de erro
    if not os.path.isfile(bin_path) or not os.access(bin_path, os.X_OK):
        print(f"Erro: {bin_path} não é um programa válido ou executável.")
        return

    # Executa o processo e monitora o tempo de CPU e o tempo de relógio
    remaining_clock_time = execute_process(bin_path, set_cpu_time, set_clock_time)

    # Enquanto houver tempo de relógio, o usuário pode executar outro binário
    while remaining_clock_time > 0:
        print(f"Tempo de relógio restante: {remaining_clock_time} segundos. Você pode executar outro programa.")
        bin_name = input("Digite o nome do próximo binário a ser executado: ").strip()
        bin_path = os.path.join("/usr/bin", bin_name)

        # Verifica se o binário é um arquivo e se é executável, se a verificação falhar, exibe uma mensagem de erro
        if not os.path.isfile(bin_path) or not os.access(bin_path, os.X_OK):
            print(f"Erro: {bin_path} não é um programa válido ou executável.")
            continue_option = input("Deseja tentar outro binário? (s/n): ").strip().lower()
            if continue_option == 'n':
                break
            else:
                continue

        # Pede a cota de CPU e o tempo de relógio
        remaining_clock_time = execute_process(bin_path, set_cpu_time, remaining_clock_time)

if __name__ == "__main__":
    main()
