from sqlalchemy import Column, Float, Integer, String, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AnalysisResult(Base):
	"""
	Model for Phasor Analysis results.
	Stores curve set, dw coefficients; fourier approximation; tau1, tau2, a1, a2 estimations
	"""
	__tablename__ = 'analysis_results'

	# meta
	id = Column(Integer, primary_key=True, autoincrement=True)
	curve_set_id = Column(Integer, ForeignKey('curve_sets.id'))
	curve_set = relationship('CurveSet')

	# Results
	dw_real = Column(ARRAY(Float))
	dw_imag = Column(ARRAY(Float))

	coeff_v = Column(Float)
	coeff_u = Column(Float)

	tau1 = Column(Float)
	tau2 = Column(Float)

	a_coeffs = Column(ARRAY(Float))

	omega = Column(Float)