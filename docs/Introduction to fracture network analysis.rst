.. image:: images/logo.png

-------------------------------------

Introduction and scope of the FracAbility library
=========================================================

Fractured rock masses are complex systems composed by intact rock and discontinuities (Hoek, 1983) . Characterizing the statistical distribution of 3D geometrical properties of such discontinuities (e.g. aperture, roughness, area, orientation, height/length ratio, etc.) is fundamental for understanding and modelling mechanical and hydraulic properties of rock masses and fluid-rock interaction.
The main obstacle that geologists encounter while trying to characterize a fractured rock volume is the impossibility of directly measuring the 3D properties of discontinuities. Because of this, a rich literature has been developed focusing on the characterization of discontinuity traces or lineaments, i.e. the 2D lines of intersection of 3D discontinuity surfaces with another surface i.e. the outcrop surface,  topography, thin section, borehole and so on.

Using the theory and logic defined in survival analysis, recently included in the SciPy package, FracAbility focuses on defining accurate length (or height) distributions based on observations carried out on natural outcrops with the Digital Outcrop approach. Particularly it shows how to properly take into consideration right censored datasets, typical of these type of observations, and how to correct them so that accurate parametrical statistical distributions can be estimated.
