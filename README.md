# Formation Control
## Descrição
Recebe informações necessárias para o controle do Ufes CloudWalker. Atualmente, o **formation control** recebe as saídas dos pacotes [*Leg Monitoring*](https://github.com/ufescloudwalker/leg_monitoring/edit/main/README.md) e [*Face Orientation*](https://github.com/ufescloudwalker/face_orientation) e é responsável por gerar as velocidades linear e angular de referência do Ufes CloudWalker. 

O controle efetuado é o **follow-in-front control**. Neste, quanto mais próximo o usuário está do andador, maior a velocidade linear, e, quanto mais longe, menor a velocidade linear. A velocidade angular é controlada pela orientação da face e o ângulo que a mesma está da orientação da câmera.

## Instalação
Não é necessária nenhuma instalação. Porém, é necessário que os pacotes  [*Leg Monitoring*](https://github.com/ufescloudwalker/leg_monitoring/edit/main/README.md) e [*Face Orientation*](https://github.com/ufescloudwalker/face_orientation) estejam funcionando de forma correta e dando os *outputs*  esperados (mencionados no *ReadMe* dos respectivos pacotes).

## Como utilizar
O repositório é dividido em:
* **config**: diretório onde se encontra o arquivo com alguns parâmetros que podem ser modificados.
* **launch**: neste diretório estão três arquivos .launch. 
	* *control_nodes_sensors*: Executa os nós do RPLidar e Usb_cam. Utilizado na Raspberry Pi para iniciar os sensores de uma vez.
	* *control_scripts*: Executa todos os scripts necessários de uma vez. Primeiro o leg_monitoring, depois o face_orientation e por último o formation_control. Os sensores devem ser inicializados antes de executar este arquivo.
	* *formation_control*: Executa apenas o script do formation_control. Para utilizar apenas este arquivo *.launch*, é necessário que leg_monitoring e face_orientation ja tenham sido executados.
* **scripts**: O script em python  responsável pelo controle do Ufes CloudWalker.

Após esse comando, 
>roslaunch formation_control formation_control.launch

o tópico turtle1/cmd_vel, *message type Twist*, é publicado e é possível observar a mudança na velocidade dependendo da orientação do rosto do usuário e a posição de suas pernas em relação ao sensor laser.

É possível ver o output pelo terminal digitando:
>rostopic echo /turtle1/cmd_vel 

## Citação
Ao utilizar este pacote, é necessário citar o trabalho abaixo. Os repositórios [formation_control](https://github.com/ufescloudwalker/formation_control), [face_orientation](https://github.com/ufescloudwalker/face_orientation) e [leg_monitoring](https://github.com/ufescloudwalker/leg_monitoring) são baseados no artigo [A novel multimodal cognitive interaction for walker-assisted rehabilitation therapies](https://ieeexplore.ieee.org/abstract/document/8779469/).

>@inproceedings{scheidegger2019novel,
  title={A novel multimodal cognitive interaction for walker-assisted rehabilitation therapies},
  author={Scheidegger, Wandercleyson M and de Mello, Ricardo C and Jimenez, Mario F and M{\'u}nera, Marcela C and Cifuentes, Carlos A and Frizera-Neto, Anselmo and others},
  booktitle={2019 IEEE 16th International Conference on Rehabilitation Robotics (ICORR)},
  pages={905--910},
  year={2019},
  organization={IEEE}
}

