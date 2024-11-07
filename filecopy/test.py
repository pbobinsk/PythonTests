import shutil, logging

#shutil.copyfile('../source/WR_S0001_Z05BO.wav', '../dest/WR_S0001_Z05BO.wav')

try:
    shutil.copy('../source/WR_S0001_Z05BO.wav', '../dest/')
except Exception as e:
    logging.error('Error',e)

