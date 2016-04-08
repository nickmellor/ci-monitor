#!flask/Scripts/python

def fileToComponentIntergrationServices(file, project, repo):
	return file.split("/")[0]

def fileToComponentDefault(file, project, repo):
	return repo

class OMSClient(object):
	
	def __init__(self):
		self.fileToComponent = {
			"MEDI_CORP:integration-services" : fileToComponentIntergrationServices,
			"OMS:api-gateway" : fileToComponentDefault
		}

	def component(self, project, repo, file):
		key = "%s:%s" % (project, repo)
		return self.fileToComponent[key](file, project, repo)

